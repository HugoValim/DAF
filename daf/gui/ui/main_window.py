from PyQt5.QtCore import QMetaObject, QObject, QRect, QSize
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QGridLayout,
    QLayout,
    QMenu,
    QMenuBar,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QWidget,
    QVBoxLayout,
)


class UiMainWindow:
    def setupUi(self, main_window):
        main_window.resize(1280, 720)
        self.central_widget = QWidget(main_window)

        self.main_v_box_layout = QVBoxLayout(self.central_widget)
        self.main_v_box_layout.setSizeConstraint(QLayout.SetDefaultConstraint)

        self.tab_widget = QTabWidget(self.central_widget)
        self.tab_widget.setMinimumSize(QSize(500, 0))
        self.main_v_box_layout.addWidget(self.tab_widget)

        main_window.setCentralWidget(self.central_widget)

        # self._set_up_menus(main_window)
        self.tab_widget.setCurrentIndex(0)

    # def _set_up_menus(self, main_window: QObject):
    #     self.menu_bar = QMenuBar()
    #     self.menu_bar.setGeometry(QRect(0, 0, 1280, 720))
    #     self.file_menu = QMenu(self.menu_bar)
    #     main_window.setMenuBar(self.menu_bar)
    #     self.status_bar = QStatusBar(main_window)
    #     main_window.setStatusBar(self.status_bar)
    #     self.new_json_template_action = QAction(main_window)
    #     self.new_json_template_action.setShortcut(QKeySequence("Ctrl+N"))
    #     self.open_json_file_action = QAction(main_window)
    #     self.open_json_file_action.setShortcut(QKeySequence("Ctrl+O"))
    #     self.export_to_filewriter_JSON_action = QAction(main_window)
    #     self.export_to_filewriter_JSON_action.setShortcut(QKeySequence("Ctrl+S"))
    #     self.export_to_nexus_action = QAction(main_window)
    #     self.export_to_compressed_filewriter_JSON_action = QAction(main_window)
    #     self.file_menu.addAction(self.new_json_template_action)
    #     self.file_menu.addAction(self.open_json_file_action)
    #     self.file_menu.addAction(self.export_to_filewriter_JSON_action)
    #     self.file_menu.addAction(self.export_to_compressed_filewriter_JSON_action)
    #     self.file_menu.addAction(self.export_to_nexus_action)

    #     self.view_menu = QMenu(self.menu_bar)
    #     self.show_action_labels = QAction(main_window)
    #     self.show_action_labels.setCheckable(True)
    #     self.show_action_labels.setChecked(True)
    #     self.simple_tree_view = QAction(main_window)
    #     self.simple_tree_view.setCheckable(True)
    #     self.about_window = QAction(main_window)
    #     self.view_menu.addAction(self.about_window)
    #     self.view_menu.addAction(self.show_action_labels)
    #     self.view_menu.addAction(self.simple_tree_view)

    #     self.menu_bar.addAction(self.file_menu.menuAction())
    #     self.menu_bar.addAction(self.view_menu.menuAction())
    #     self._set_up_titles(main_window)

    # def _set_up_titles(self, main_window):
    #     self.menu_bar.setNativeMenuBar(False)
    #     main_window.setWindowTitle("NeXus Constructor")
    #     self.tab_widget.setTabText(
    #         self.tab_widget.indexOf(self.component_tree_view_tab), "Nexus Structure"
    #     )
    #     self.tab_widget.setTabText(
    #         self.tab_widget.indexOf(self.camera_settings_tab), "Camera Settings"
    #     )
    #     self.tab_widget.setTabText(
    #         self.tab_widget.indexOf(self.render_settings_tab), "Render Settings"
    #     )
    #     self.file_menu.setTitle("File")
    #     self.new_json_template_action.setText("Create new NeXus JSON template")
    #     self.open_json_file_action.setText("Open File writer JSON file")
    #     self.export_to_filewriter_JSON_action.setText("Export to file writer JSON")
    #     self.export_to_compressed_filewriter_JSON_action.setText(
    #         "Export to compressed file writer JSON"
    #     )
    #     self.export_to_nexus_action.setText("Export to NeXus file")

    #     self.view_menu.setTitle("View")
    #     self.show_action_labels.setText("Show Button Labels")
    #     self.simple_tree_view.setText("Use Simple Tree Model View")
    #     self.about_window.setText("About")
