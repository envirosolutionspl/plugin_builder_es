def templates():
    from .toolbutton_with_dialog.plugin_template import ToolbuttonWithDialogPluginTemplate
    from .toolbutton_with_dockwidget.plugin_template import ToolbuttonWithDockWidgetPluginTemplate
    # Pierwszy na liście jest domyślnie wybrany w kreatorze.
    return [
        ToolbuttonWithDockWidgetPluginTemplate(),
        ToolbuttonWithDialogPluginTemplate(),
    ]
