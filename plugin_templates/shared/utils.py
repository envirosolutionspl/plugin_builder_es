from qgis.core import (
    Qgis,
    QgsApplication,
    QgsMessageLog,
    QgsNetworkAccessManager,
    QgsBlockingNetworkRequest
)
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager 
from qgis.PyQt.QtGui import QIcon, QPalette, QPixmap
from qgis.PyQt.QtCore import Qt, QUrl, QUrlQuery, QEventLoop, QTimer, QT_VERSION_STR, QCoreApplication
from qgis.PyQt.QtWidgets import QMessageBox, QWidget

from . import PLUGIN_NAME
from .constants import (
    QT_VER,
    NETWORK_ATTRS,
    ERR_TIMEOUT,
    ERR_NONE,
    ERR_CANCELED,
    MSG_DOWNLOAD_CANCELED,
    MSG_NETWORK_ERROR,
    MSG_HTTP_ERROR,
    MSG_EMPTY_CONTENT,
    MSG_TIMEOUT,
    MSG_FILE_WRITE_ERROR,
    TIMEOUT_MS,
    CANCEL_CHECK_MS,
    HTTP_ERROR_THRESHOLD,
    REDIRECT_POLICY_NAME,
    REDIRECT_POLICY_NO_LESS_SAFE,
    DEFAULT_REDIRECT_POLICY,
    DEFAULT_ENCODING
)

from functools import partial
import configparser
import os
import re

PLUGIN_DIR = os.path.dirname(__file__)

class TranslationUtils:
    @staticmethod
    def tr(message):
        return QCoreApplication.translate("TranslationUtils", message)


class ThemeUtils:
    """Motyw jasny/ciemny okien wtyczki. Kolory są w arkuszach stylów .ui (selektory [theme="..."])."""

    @staticmethod
    def isDarkTheme():
        name = (QgsApplication.themeName() or '').lower()
        if 'night' in name or 'dark' in name:
            return True
        return QgsApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128

    @staticmethod
    def repolishAll(window):
        """Po zmianie właściwości "theme" - widgety mogły zostać ostylowane wcześniej."""
        for widget in [window] + window.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    @staticmethod
    def setLogo(label, filename, height):
        pix = QPixmap(os.path.join(PLUGIN_DIR, 'images', filename))
        if pix.isNull():
            MessageUtils.pushLogWarning(f"Nie znaleziono pliku logo: images/{filename}")
            return
        # Skalowanie z uwzględnieniem skali ekranu, inaczej logo jest rozpikselowane przy 125-150%.
        dpr = label.devicePixelRatioF()
        pix = pix.scaledToHeight(int(height * dpr), Qt.TransformationMode.SmoothTransformation)
        pix.setDevicePixelRatio(dpr)
        label.setScaledContents(False)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(pix)

    @staticmethod
    def setLinkColor(labels, color):
        for label in labels:
            label.setText(re.sub(r'style="[^"]*"',
                                 'style="text-decoration:underline; color:%s;"' % color,
                                 label.text()))

    @staticmethod
    def readHomepage():
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read(os.path.join(PLUGIN_DIR, 'metadata.txt'), encoding='utf-8')
        except UnicodeDecodeError as e:
            MessageUtils.pushLogWarning(f"Nie można odczytać metadata.txt - złe kodowanie (UnicodeDecodeError): {e}")
            return ''
        except configparser.Error as e:
            MessageUtils.pushLogWarning(f"Błędny format metadata.txt ({type(e).__name__}): {e}")
            return ''
        return parser.get('general', 'homepage', fallback='')


class MessageUtils:
    """
    Klasa pomocnicza do obsługi komunikatów UI oraz logowania w QGIS.

    Zawiera metody do wyświetlania okien dialogowych (QMessageBox),
    komunikatów w pasku wiadomości (messageBar) oraz logów systemowych.

    Metody są statyczne,klasa nie wymaga instancjonowania.
    """

    @staticmethod
    def pushMessageBoxCritical(parent, title: str, message: str):
        msg_box = QMessageBox(
            QMessageBox.Icon.Critical,
            title,
            message,
            QMessageBox.StandardButton.Ok,
            parent
        )
        if hasattr(parent, 'plugin_icon'):
            msg_box.setWindowIcon(QIcon(parent.plugin_icon))
        msg_box.exec()

    @staticmethod
    def pushMessageBoxInfo(parent, title, message):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        if hasattr(parent, 'plugin_icon'):
            msg_box.setWindowIcon(QIcon(parent.plugin_icon))

        msg_box.exec()

    @staticmethod
    def pushMessageBoxYesNo(parent, title, message):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes

    @staticmethod
    def pushMessage(iface, message: str) -> None:
        iface.messageBar().pushMessage(
            'Informacja',
            message,
            level=Qgis.Info,
            duration=10
        )

    @staticmethod
    def pushSuccess(iface, message: str) -> None:
        iface.messageBar().pushMessage(
            "Sukces",
            message,
            level=Qgis.Success,
            duration=0
        )

    @staticmethod
    def pushWarning(iface, message: str) -> None:
        iface.messageBar().pushMessage(
            'Ostrzeżenie',
            message,
            level=Qgis.Warning,
            duration=10
        )

    @staticmethod
    def pushLogInfo(message: str) -> None:
        QgsMessageLog.logMessage(
            message,
            tag=PLUGIN_NAME,
            level=Qgis.Info
        )

    @staticmethod
    def pushLogWarning(message: str) -> None:
        QgsMessageLog.logMessage(
            message,
            tag=PLUGIN_NAME,
            level=Qgis.Warning
        )

    @staticmethod
    def pushLogCritical(message: str) -> None:
        QgsMessageLog.logMessage(
            message,
            tag=PLUGIN_NAME,
            level=Qgis.Critical
        )

class VersionUtils:
    """
    Klasa pomocnicza do sprawdzania kompatybilności wersji Qt.

    Nie wymaga instancjonowania.
    """
    @staticmethod
    def isCompatibleQtVersion(tar_version):
        return QT_VERSION_STR.startswith(QT_VER[tar_version])

class NetworkUtils:
    """
    Klasa do obsługi operacji sieciowych w QGIS.

    Zapewnia:
    - pobieranie danych tekstowych (fetchContent)
    - pobieranie plików (downloadFile)
    - obsługę błędów HTTP i sieciowych
    - kompatybilność z Qt5/Qt6
    - wsparcie dla anulowania operacji (QgsTask)

    Wykorzystuje:
    - QNetworkAccessManager (asynchroniczne operacje)
    - QgsBlockingNetworkRequest (operacje blokujące)
    """
    
    def __init__(self):
        self.manager = QNetworkAccessManager()
        self.manager.setProxy(QgsNetworkAccessManager.instance().proxy())

    def _handleReplyError(self, reply, url_str):
        """Centralna obsługa błędów sieciowych i HTTP"""
        
        error_code = reply.error()
        error_str = reply.errorString()
        
        status_attr = self._getAttributeEnum(NETWORK_ATTRS['HTTP_STATUS'])
        reason_attr = self._getAttributeEnum(NETWORK_ATTRS['HTTP_REASON'])
        timeout_err = self._getErrorEnum(ERR_TIMEOUT)

        http_status = reply.attribute(status_attr)
        http_reason = reply.attribute(reason_attr)
        
        if http_status and http_status >= HTTP_ERROR_THRESHOLD:
            return False, MSG_HTTP_ERROR.format(http_status, http_reason)
        
        if error_code == timeout_err:
            return False, MSG_TIMEOUT.format(url_str)
            
        return False, MSG_NETWORK_ERROR.format(error_str, url_str)

    def _hasErrorOccurred(self, reply):
        """Sprawdza czy wystąpił błąd w odpowiedzi"""
        no_error = self._getErrorEnum(ERR_NONE)
        return reply.error() != no_error

    def _getAttributeEnum(self, attr_name):
        """Pobiera atrybut QNetworkRequest"""
        if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
            if hasattr(QNetworkRequest, 'Attribute'):
                val = getattr(QNetworkRequest.Attribute, attr_name, None)
                if val is not None:
                    return val
        return getattr(QNetworkRequest, attr_name, None)

    def _getErrorEnum(self, attr_name):
        """Pobiera kod błędu QNetworkReply"""
        if VersionUtils.isCompatibleQtVersion(QT_VERSION_STR, 6):
            if hasattr(QNetworkReply, 'NetworkError'):
                val = getattr(QNetworkReply.NetworkError, attr_name, None)
                if val is not None:
                    return val
        return getattr(QNetworkReply, attr_name, None)

    def _setAttributes(self, request, timeout_ms):
        """Ustawia atrybuty zapytania"""
        redirect_attr = self._getAttributeEnum(NETWORK_ATTRS['REDIRECT'])
        if redirect_attr is not None:
            redirect_policy_class = getattr(QNetworkRequest, REDIRECT_POLICY_NAME, QNetworkRequest)
            redirect_policy = getattr(redirect_policy_class, REDIRECT_POLICY_NO_LESS_SAFE, DEFAULT_REDIRECT_POLICY)
            request.setAttribute(redirect_attr, redirect_policy)
        
        timeout_attr = self._getAttributeEnum(NETWORK_ATTRS['TIMEOUT'])
        if timeout_attr is not None:
            request.setAttribute(timeout_attr, timeout_ms)
            
    def fetchContent(self, url, params=None, timeout_ms=TIMEOUT_MS):
        """Pobiera zawartość z podanego URL. Wykorzystuje QgsBlockingNetworkRequest.

        Parametry:
        - url (str): adres URL, z którego pobieramy dane.
        - params (dict, opcjonalnie): słownik parametrów zapytania GET, które zostaną dołączone do URL.
        - timeout_ms (int, opcjonalnie): czas oczekiwania na odpowiedź w milisekundach.

        Zwraca:
        - Tuple (success, data_or_message):
            - success (bool): True jeśli pobranie się powiodło, False w przypadku błędu lub pustej odpowiedzi.
            - data_or_message (str): zawartość odpowiedzi w formie tekstu, informacja o danych binarnych, lub komunikat o błędzie.
        """
        q_url = QUrl(url)
        if params:
            query = QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(str(key), str(value))
            q_url.setQuery(query)
            
        request = QNetworkRequest(q_url)
        self._setAttributes(request, timeout_ms)
        
        blocking_request = QgsBlockingNetworkRequest()
        error_code = blocking_request.get(request)
        reply_content = blocking_request.reply()
        
        if error_code != QgsBlockingNetworkRequest.NoError:
            return self._handleReplyError(reply_content, url)

        raw_data = reply_content.content()
        if len(raw_data) == 0:
            return False, MSG_EMPTY_CONTENT.format(url)
            
        try:
            data = bytes(raw_data).decode(DEFAULT_ENCODING)
            return True, data
        except UnicodeDecodeError:
            return True, f"BinaryData: {len(raw_data)} bytes"
  
    def downloadFile(self, url, dest_path, obj=None, timeout_ms=TIMEOUT_MS):
        """
        Pobieranie pliku z podanego URL. Bezpieczne dla wielowątkowości i QgsTasks.

        Parametry:
        - url (str): adres URL, z którego pobieramy plik.
        - dest_path (str): ścieżka do pliku, w którym zostanie zapisany pobrany plik.
        - obj (QgsTask, opcjonalnie): obiekt QgsTask, który zostanie wykorzystany do sprawdzania statusu anulowania.
        - timeout_ms (int, opcjonalnie): czas oczekiwania na odpowiedź w milisekundach.

        Zwraca:
        - Tuple (success, result):
            - success (bool): True jeśli pobranie się powiodło, False w przypadku błędu lub anulowania.
            - result (bool | str):
                - True w przypadku sukcesu,
                - komunikat błędu (str) w przypadku niepowodzenia.
        """
        request = QNetworkRequest(QUrl(url))
        self._setAttributes(request, timeout_ms)

        dest_dir = os.path.dirname(dest_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        event_loop = QEventLoop()
        reply = self.manager.get(request)
        try:
            with open(dest_path, 'wb') as f:
                reply.readyRead.connect(partial(self._handleReadyRead, reply, f))
                reply.finished.connect(event_loop.quit)

                self._loopForCancel(obj, reply, event_loop)

                if reply.bytesAvailable() > 0:
                    f.write(reply.readAll().data())
        except IOError as e:
            return False, MSG_FILE_WRITE_ERROR.format(str(e))
            
        return self._finalizeDownload(reply, url)
    
    def _handleReadyRead(self, reply, file):
        if reply.bytesAvailable() > 0:
            file.write(reply.readAll().data())

    def _loopForCancel(self, obj, reply, event_loop):
        cancel_timer = QTimer()
        cancel_timer.timeout.connect(lambda: reply.abort() if (obj and obj.isCanceled()) else None)
        cancel_timer.start(CANCEL_CHECK_MS)
        
        event_loop.exec()

        cancel_timer.stop()
    
    def _finalizeDownload(self, reply, url):
        if self._hasErrorOccurred(reply):
            canceled_error = self._getErrorEnum(ERR_CANCELED)
            if reply.error() == canceled_error:
                reply.deleteLater()
                return False, MSG_DOWNLOAD_CANCELED
            
            error_res = self._handleReplyError(reply, url)
            reply.deleteLater()
            return error_res

        reply.deleteLater()
        return True, True

