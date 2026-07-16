"""Layout definitions for the financial information panel."""

import urllib.parse
import urllib.request
from typing import Dict, Any, List
from qtpy import QtCore, QtGui, QtWidgets
from data_engine import MarketDataEngine

FONT_FAMILY = "Inter, system-ui, -apple-system, sans-serif"


class OverviewMetricsGrid(QtWidgets.QWidget):
    """Custom component hosting a structured three-column financial KPI grid layout."""

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setHorizontalSpacing(35)
        self.grid_layout.setVerticalSpacing(14)

    def populate_metrics(self, metrics: Dict[str, str]) -> None:
        """Draws key-value items sequentially into dedicated columns."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        col1_items = ["Open", "High", "Low", "Mkt cap"]
        col2_items = ["Avg. vol.", "Volume", "P/E ratio", "52-wk high"]
        col3_items = ["52-wk low", "EPS", "Shares outstanding", "No. of employees"]

        self._render_column_block(col1_items, metrics, target_grid_col=0)
        self._render_column_block(col2_items, metrics, target_grid_col=2)
        self._render_column_block(col3_items, metrics, target_grid_col=4)

    def _render_column_block(
        self, target_keys: List[str], data: dict, target_grid_col: int
    ) -> None:
        for idx, key in enumerate(target_keys):
            val_text = data.get(key, "-")

            lbl_key = QtWidgets.QLabel(key)
            lbl_key.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #5f6368; font-size: 13px; font-weight: 500;"
            )

            lbl_val = QtWidgets.QLabel(val_text)
            lbl_val.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #202124; font-size: 13px; font-weight: bold;"
            )
            lbl_val.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

            self.grid_layout.addWidget(lbl_key, idx, target_grid_col)
            self.grid_layout.addWidget(lbl_val, idx, target_grid_col + 1)


class CorporateAboutPanel(QtWidgets.QWidget):
    """Visualizes business descriptions and metadata points without internal scrollbars."""

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.layout.setSpacing(12)

        self.lbl_section_title = QtWidgets.QLabel("About")
        self.lbl_section_title.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 16px; font-weight: bold; color: #202124;"
        )
        self.layout.addWidget(self.lbl_section_title)

        self.lbl_description = QtWidgets.QLabel()
        self.lbl_description.setStyleSheet(
            f"font-family: {FONT_FAMILY}; color: #3c4043; font-size: 13px; line-height: 20px;"
        )
        self.lbl_description.setWordWrap(True)
        self.layout.addWidget(self.lbl_description)

        self.info_grid = QtWidgets.QGridLayout()
        self.info_grid.setHorizontalSpacing(30)
        self.info_grid.setVerticalSpacing(10)
        self.layout.addLayout(self.info_grid)

    def populate_about(self, about_data: Dict[str, Any]) -> None:
        """Populates company profile parameters."""
        self.lbl_description.setText(about_data["description"])

        while self.info_grid.count():
            item = self.info_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        fields = [
            ("CEO", about_data["CEO"]),
            ("Headquarters", about_data["Headquarters"]),
            ("Employees", about_data["Employees"]),
            ("Website", about_data["Website"]),
        ]

        for idx, (label, val) in enumerate(fields):
            lbl_title = QtWidgets.QLabel(label)
            lbl_title.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #5f6368; font-size: 13px; font-weight: 500;"
            )

            lbl_content = QtWidgets.QLabel(str(val))
            lbl_content.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #202124; font-size: 13px; font-weight: bold;"
            )

            self.info_grid.addWidget(lbl_title, idx, 0)
            self.info_grid.addWidget(lbl_content, idx, 1)


class NewsFeedPanel(QtWidgets.QWidget):
    """Displays multi-column interactive financial articles with global font controls."""

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.layout.setSpacing(15)

        self.lbl_news_title = QtWidgets.QLabel("Latest News")
        self.lbl_news_title.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 16px; font-weight: bold; color: #202124;"
        )
        self.layout.addWidget(self.lbl_news_title)

        self.grid_container = QtWidgets.QGridLayout()
        self.grid_container.setHorizontalSpacing(24)
        self.grid_container.setVerticalSpacing(20)
        self.layout.addLayout(self.grid_container)

    def populate_news(self, articles: List[Dict[str, str]]) -> None:
        """Assembles a fine-tuned two-column grid using precise typography overrides."""
        while self.grid_container.count():
            item = self.grid_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not articles:
            lbl_empty = QtWidgets.QLabel("No recent news headlines resolved.")
            lbl_empty.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #70757a; font-style: italic; font-size: 13px;"
            )
            self.grid_container.addWidget(lbl_empty, 0, 0)
            return

        for idx, item in enumerate(articles):
            row = idx // 2
            col = idx % 2

            tile = QtWidgets.QWidget()
            tile_lay = QtWidgets.QVBoxLayout(tile)
            tile_lay.setContentsMargins(0, 0, 0, 0)
            tile_lay.setSpacing(4)

            meta_row = QtWidgets.QHBoxLayout()
            meta_row.setSpacing(6)
            meta_row.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
            )

            lbl_logo = QtWidgets.QLabel()
            lbl_logo.setFixedSize(16, 16)
            lbl_logo.setScaledContents(True)
            self._async_load_favicon(item["logo_url"], lbl_logo)
            meta_row.addWidget(lbl_logo)

            lbl_pub = QtWidgets.QLabel(item["publisher"])
            lbl_pub.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #202124; font-size: 13px; font-weight: bold;"
            )
            meta_row.addWidget(lbl_pub)

            lbl_dot = QtWidgets.QLabel("·")
            lbl_dot.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #70757a; font-size: 13px; font-weight: bold;"
            )
            meta_row.addWidget(lbl_dot)

            lbl_time = QtWidgets.QLabel(item["time"])
            lbl_time.setStyleSheet(
                f"font-family: {FONT_FAMILY}; color: #70757a; font-size: 13px; font-weight: bold;"
            )
            meta_row.addWidget(lbl_time)
            tile_lay.addLayout(meta_row)

            lbl_headline = QtWidgets.QLabel()
            lbl_headline.setText(
                f'<a href="{item["link"]}" style="text-decoration: none; color: #1a73e8;">{item["title"]}</a>'
            )
            lbl_headline.setOpenExternalLinks(True)
            lbl_headline.setWordWrap(True)
            lbl_headline.setStyleSheet(f"""
                QLabel {{
                    font-family: {FONT_FAMILY};
                    font-size: 12px;
                    font-weight: 400;
                }}
                QLabel:hover {{
                    text-decoration: underline;
                }}
            """)
            tile_lay.addWidget(lbl_headline)

            self.grid_container.addWidget(tile, row, col)

    def _async_load_favicon(self, url: str, target_label: QtWidgets.QLabel) -> None:
        """Fetches brand imagery safely via the network layer context."""
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                img_bytes = response.read()

            pixmap = QtGui.QPixmap()
            if pixmap.loadFromData(img_bytes):
                target_label.setPixmap(pixmap)
                return
        except Exception:
            pass

        default_dot = QtGui.QPixmap(16, 16)
        default_dot.fill(QtGui.QColor("#bdc1c6"))
        target_label.setPixmap(default_dot)


class MainOverviewWorkspace(QtWidgets.QWidget):
    """Houses composite metrics grids, corporate backgrounds, and news items."""

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: transparent; font-family: {FONT_FAMILY}; }}
            QScrollBar:vertical {{
                border: none; background: #e8eaed; width: 12px; margin: 0px; border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{ background: #b8bbbe; min-height: 30px; border-radius: 6px; }}
            QScrollBar::handle:vertical:hover {{ background: #9aa0a6; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ background: none; height: 0px; }}
        """)

        content_container = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(content_container)
        self.content_layout.setContentsMargins(0, 0, 12, 0)
        self.content_layout.setSpacing(15)

        self.metrics_grid = OverviewMetricsGrid(self)
        self.about_panel = CorporateAboutPanel(self)
        self.news_panel = NewsFeedPanel(self)

        self.content_layout.addWidget(self.metrics_grid)
        self.content_layout.addWidget(self._create_divider())
        self.content_layout.addWidget(self.news_panel)
        self.content_layout.addWidget(self._create_divider())
        self.content_layout.addWidget(self.about_panel)

        scroll.setWidget(content_container)
        layout.addWidget(scroll)

    def _create_divider(self) -> QtWidgets.QFrame:
        div = QtWidgets.QFrame()
        div.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        div.setStyleSheet("background-color: #dadce0; max-height: 1px; border: none;")
        return div

    def populate_all(self, ticker: Any) -> None:
        """Pushes data downstream to dashboard components."""
        self.metrics_grid.populate_metrics(
            MarketDataEngine.extract_overview_metrics(ticker)
        )
        self.about_panel.populate_about(
            MarketDataEngine.extract_about_and_profile(ticker)
        )
        self.news_panel.populate_news(MarketDataEngine.extract_news_feed(ticker))


class EarningsWorkspace(QtWidgets.QWidget):
    """Component handling corporate accounting details for the Earnings tab."""

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.layout.setSpacing(15)

        self.lbl_title = QtWidgets.QLabel("Quarterly Earnings Performance")
        self.lbl_title.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 16px; font-weight: bold; color: #202124;"
        )
        self.layout.addWidget(self.lbl_title)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Quarterly Period", "Total Revenue", "Net Income / Earnings"]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        # FIXED: Hide index rows natively to eliminate row indexes (1, 2, 3) from the canvas view
        self.table.verticalHeader().setVisible(False)

        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                background-color: transparent;
            }}
            QHeaderView::section {{
                background-color: #f8f9fa;
                color: #5f6368;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #dadce0;
                font-size: 13px;
            }}
        """)
        self.layout.addWidget(self.table)
        self.layout.addStretch()

    def populate_earnings_grid(
        self, dataset: List[Dict[str, Any]], currency_code: str
    ) -> None:
        """Binds quarterly parameters using safe QTableWidgetItem setters."""
        self.table.setRowCount(0)
        if not dataset:
            return

        self.table.setRowCount(len(dataset))
        symbol = "₹" if currency_code == "INR" else "$"

        # Instantiate proper Typography elements to override setStyleSheet limits
        cell_font = QtGui.QFont("Inter", 10)
        bold_font = QtGui.QFont("Inter", 10, QtGui.QFont.Weight.Bold)

        for idx, item in enumerate(dataset):
            rev_txt = (
                f"{symbol}{item['Revenue']:,.2f}"
                if item["Revenue"] is not None
                else "—"
            )
            earn_txt = (
                f"{symbol}{item['Earnings']:,.2f}"
                if item["Earnings"] is not None
                else "—"
            )

            cell_period = QtWidgets.QTableWidgetItem(item["Period"])
            cell_revenue = QtWidgets.QTableWidgetItem(rev_txt)
            cell_earnings = QtWidgets.QTableWidgetItem(earn_txt)

            # Alignment bindings
            cell_revenue.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            cell_earnings.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )

            # FIXED: Migrated visual parameters to native .setFont() and .setForeground() calls
            cell_period.setFont(cell_font)
            cell_period.setForeground(QtGui.QBrush(QtGui.QColor("#202124")))

            cell_revenue.setFont(cell_font)
            cell_revenue.setForeground(QtGui.QBrush(QtGui.QColor("#202124")))

            cell_earnings.setFont(bold_font)
            if item["Earnings"] is not None:
                if item["Earnings"] >= 0:
                    cell_earnings.setForeground(QtGui.QBrush(QtGui.QColor("#137333")))
                else:
                    cell_earnings.setForeground(QtGui.QBrush(QtGui.QColor("#c5221f")))
            else:
                cell_earnings.setFont(cell_font)
                cell_earnings.setForeground(QtGui.QBrush(QtGui.QColor("#5f6368")))

            self.table.setItem(idx, 0, cell_period)
            self.table.setItem(idx, 1, cell_revenue)
            self.table.setItem(idx, 2, cell_earnings)


class FinancialsWorkspace(QtWidgets.QWidget):
    """Component handling annual income statements for the Financials tab."""

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.layout.setSpacing(15)

        self.lbl_title = QtWidgets.QLabel("Annual Balance Metrics & Income Statement")
        self.lbl_title.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 16px; font-weight: bold; color: #202124;"
        )
        self.layout.addWidget(self.lbl_title)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Fiscal Year", "Gross Revenue", "Operating Expenses", "Net Income"]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                background-color: transparent;
            }}
            QHeaderView::section {{
                background-color: #f8f9fa;
                color: #5f6368;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #dadce0;
                font-size: 13px;
            }}
        """)
        self.layout.addWidget(self.table)
        self.layout.addStretch()

    def populate_financials_grid(
        self, dataset: List[Dict[str, Any]], currency_code: str
    ) -> None:
        """Binds annual statement records using safe QTableWidgetItem setters."""
        self.table.setRowCount(0)
        if not dataset:
            return

        self.table.setRowCount(len(dataset))
        symbol = "₹" if currency_code == "INR" else "$"

        cell_font = QtGui.QFont("Inter", 10)
        bold_font = QtGui.QFont("Inter", 10, QtGui.QFont.Weight.Bold)

        for idx, item in enumerate(dataset):
            rev_txt = (
                f"{symbol}{item['Total Revenue']:,.2f}"
                if item["Total Revenue"] is not None
                else "—"
            )
            exp_txt = (
                f"{symbol}{item['Operating Expenses']:,.2f}"
                if item["Operating Expenses"] is not None
                else "—"
            )
            net_txt = (
                f"{symbol}{item['Net Income']:,.2f}"
                if item["Net Income"] is not None
                else "—"
            )

            cell_year = QtWidgets.QTableWidgetItem(item["Year"])
            cell_revenue = QtWidgets.QTableWidgetItem(rev_txt)
            cell_expenses = QtWidgets.QTableWidgetItem(exp_txt)
            cell_net = QtWidgets.QTableWidgetItem(net_txt)

            # Align elements symmetrically
            cell_revenue.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            cell_expenses.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            cell_net.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )

            # Apply font definitions securely
            for cell in [cell_year, cell_revenue, cell_expenses]:
                cell.setFont(cell_font)
                cell.setForeground(QtGui.QBrush(QtGui.QColor("#202124")))

            cell_net.setFont(bold_font)
            if item["Net Income"] is not None:
                if item["Net Income"] >= 0:
                    cell_net.setForeground(QtGui.QBrush(QtGui.QColor("#137333")))
                else:
                    cell_net.setForeground(QtGui.QBrush(QtGui.QColor("#c5221f")))
            else:
                cell_net.setFont(cell_font)
                cell_net.setForeground(QtGui.QBrush(QtGui.QColor("#5f6368")))

            self.table.setItem(idx, 0, cell_year)
            self.table.setItem(idx, 1, cell_revenue)
            self.table.setItem(idx, 2, cell_expenses)
            self.table.setItem(idx, 3, cell_net)


class DashboardFrame(QtWidgets.QFrame):
    """Integrated multi-tab dashboard analytics tracking panel."""

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self._active_ticker = None
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)

        self.setStyleSheet(f"""
            DashboardFrame {{
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 8px;
                font-family: {FONT_FAMILY};
            }}
            QWidget {{
                font-family: {FONT_FAMILY};
            }}
        """)
        self._init_ui()

    def _init_ui(self) -> None:
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 1. Search Panel Block
        search_layout = QtWidgets.QHBoxLayout()
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Search symbols (e.g. DIXON.NS, MSFT)...")
        self.search_box.setMinimumHeight(40)

        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #dadce0; border-radius: 20px; padding-left: 15px; padding-right: 15px; font-size: 14px; font-family: {FONT_FAMILY}; background-color: #f1f3f4; color: #202124;
            }}
            QLineEdit:focus {{ border: 1px solid #1a73e8; background-color: #ffffff; }}
        """)
        self.search_box.returnPressed.connect(self.trigger_search)

        self.btn_search = QtWidgets.QPushButton("Search")
        self.btn_search.setMinimumHeight(40)
        self.btn_search.setMinimumWidth(100)

        self.btn_search.setStyleSheet(f"""
            QPushButton {{
                background-color: #1a73e8; color: #ffffff; border: none; border-radius: 20px; font-size: 14px; font-weight: bold; font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{ background-color: #1557b0; }}
        """)
        self.btn_search.clicked.connect(self.trigger_search)

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.btn_search)
        self.main_layout.addLayout(search_layout)

        # 2. Financial Metrics Header Widget
        self.header_widget = QtWidgets.QWidget()
        header_lay = QtWidgets.QVBoxLayout(self.header_widget)
        header_lay.setContentsMargins(0, 5, 0, 5)
        header_lay.setSpacing(4)

        self.lbl_company_name = QtWidgets.QLabel("Market Intelligence Dashboard")
        self.lbl_company_name.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 22px; font-weight: bold; color: #202124;"
        )

        price_row = QtWidgets.QHBoxLayout()
        self.lbl_price = QtWidgets.QLabel("—")
        self.lbl_price.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 28px; font-weight: bold; color: #202124;"
        )

        self.lbl_change = QtWidgets.QLabel("")
        self.lbl_change.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 15px; font-weight: bold; margin-left: 10px;"
        )

        price_row.addWidget(self.lbl_price)
        price_row.addWidget(self.lbl_change)
        price_row.addStretch()

        self.lbl_timestamp = QtWidgets.QLabel("Enter a symbol to populate market data")
        self.lbl_timestamp.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 12px; color: #5f6368;"
        )

        header_lay.addWidget(self.lbl_company_name)
        header_lay.addLayout(price_row)
        header_lay.addWidget(self.lbl_timestamp)
        self.main_layout.addWidget(self.header_widget)

        # 3. Dynamic Tab Bar System (Assembling Part 2 & Part 3 simultaneously)
        self.tab_container = QtWidgets.QTabBar()
        self.tab_container.addTab("Overview")
        self.tab_container.addTab("Earnings")
        self.tab_container.addTab("Financials")

        self.tab_container.setStyleSheet(f"""
            QTabBar::tab {{
                font-family: {FONT_FAMILY}; font-size: 14px; font-weight: bold; color: #5f6368; padding: 10px 20px; border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; }}
        """)
        self.tab_container.currentChanged.connect(self._handle_tab_switches)
        self.main_layout.addWidget(self.tab_container)

        # Divider line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #dadce0; max-height: 1px; border: none;")
        self.main_layout.addWidget(line)

        # 4. Content Stack Shell Window Layout Management
        self.stack_layout = QtWidgets.QStackedWidget()
        self.overview_workspace = MainOverviewWorkspace(self)
        self.earnings_workspace = EarningsWorkspace(self)
        self.financials_workspace = FinancialsWorkspace(self)

        self.stack_layout.addWidget(self.overview_workspace)
        self.stack_layout.addWidget(self.earnings_workspace)
        self.stack_layout.addWidget(self.financials_workspace)
        self.main_layout.addWidget(self.stack_layout)

    def _handle_tab_switches(self, target_index: int) -> None:
        """Manages tab transitions over the central dashboard frame view stack."""
        self.stack_layout.setCurrentIndex(target_index)
        if not self._active_ticker:
            return

        currency = self._active_ticker.info.get("currency", "USD")
        if target_index == 1:
            earnings_dataset = MarketDataEngine.extract_earnings_history(
                self._active_ticker
            )
            self.earnings_workspace.populate_earnings_grid(earnings_dataset, currency)
        elif target_index == 2:
            financials_dataset = MarketDataEngine.extract_financial_statements(
                self._active_ticker
            )
            self.financials_workspace.populate_financials_grid(
                financials_dataset, currency
            )

    def trigger_search(self) -> None:
        """Extracts text inputs, executes validation checks, and triggers updates."""
        symbol = self.search_box.text()
        if not symbol.strip():
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            is_valid, ticker, _ = MarketDataEngine.validate_and_fetch_ticker(symbol)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        if not is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                "Symbol Resolution Error",
                f"The symbol '{symbol}' was not found.\nPlease enter a valid ticker.",
            )
            return

        self._active_ticker = ticker
        self._load_ticker_view(ticker)

        self.tab_container.setCurrentIndex(0)
        self.stack_layout.setCurrentIndex(0)

    def _load_ticker_view(self, ticker: yf.Ticker) -> None:
        """Processes and maps raw market payloads to UI visual assets."""
        try:
            header_data = MarketDataEngine.extract_header_metrics(ticker)
            self.lbl_company_name.setText(header_data["name"])

            currency_lbl = "$" if header_data["currency"] != "INR" else "₹"
            self.lbl_price.setText(f"{currency_lbl}{header_data['price']:,.2f}")

            change_prefix = "+" if header_data["change_abs"] >= 0 else ""
            self.lbl_change.setText(
                f"{change_prefix}{header_data['change_abs']:,.2f} ({change_prefix}{header_data['change_pct']:.2f}%)"
            )

            if header_data["change_abs"] >= 0:
                self.lbl_change.setStyleSheet(
                    f"font-family: {FONT_FAMILY}; font-size: 15px; font-weight: bold; color: #137333;"
                )
            else:
                self.lbl_change.setStyleSheet(
                    f"font-family: {FONT_FAMILY}; font-size: 15px; font-weight: bold; color: #c5221f;"
                )

            self.lbl_timestamp.setText(
                f"{header_data['last_updated']} · {header_data['currency']}"
            )
            self.overview_workspace.populate_all(ticker)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Data Extraction Warning", f"Parsing error occurred: {e}"
            )
