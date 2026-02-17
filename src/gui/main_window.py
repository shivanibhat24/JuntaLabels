"""
PyQt6 GUI for Sustainability Deception Detector
Provides intuitive interface for image upload and camera capture
"""

import sys
import os
from pathlib import Path
from typing import Optional
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QTabWidget,
    QProgressBar, QScrollArea, QFrame, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from detector import SustainabilityDetector
except ImportError:
    # Fallback for testing
    SustainabilityDetector = None


class AnalysisThread(QThread):
    """Background thread for analysis to prevent GUI freezing"""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    
    def __init__(self, detector, image_path: str, parent=None):
        super().__init__(parent)
        self.detector = detector
        self.image_path = image_path
    
    def run(self):
        """Run analysis in background"""
        try:
            self.progress.emit(10, "Initializing analysis...")
            
            self.progress.emit(30, "Performing computer vision analysis...")
            # Analysis happens here
            result = self.detector.analyze_image(self.image_path)
            
            self.progress.emit(90, "Generating report...")
            
            if result.get('success', False):
                self.finished.emit(result)
            else:
                self.error.emit(result.get('error', 'Unknown error occurred'))
                
        except Exception as e:
            self.error.emit(f"Analysis error: {str(e)}")


class SustainabilityDetectorGUI(QMainWindow):
    """Main GUI window"""
    
    def __init__(self):
        super().__init__()
        self.detector = None
        self.current_image_path = None
        self.current_report = None
        
        self.init_ui()
        self.init_detector()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Sustainability Deception Detector")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set modern color scheme
        self.set_theme()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Input and controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # Right panel - Results
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=2)
        
        self.statusBar().showMessage("Ready")
    
    def set_theme(self):
        """Set modern dark/light theme"""
        palette = QPalette()
        
        # Modern color scheme
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 245))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 250))
        palette.setColor(QPalette.ColorRole.Button, QColor(76, 175, 80))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        
        self.setPalette(palette)
    
    def create_left_panel(self) -> QWidget:
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🌍 Sustainability Deception Detector")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Detect Greenwashing • Brownwashing • Bluewashing")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Image preview
        preview_group = QGroupBox("Product Image")
        preview_layout = QVBoxLayout(preview_group)
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setMaximumSize(400, 400)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        preview_layout.addWidget(self.image_label)
        
        layout.addWidget(preview_group)
        
        # Input buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # Upload button
        self.upload_btn = QPushButton("📁 Upload Image")
        self.upload_btn.setMinimumHeight(50)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_image)
        button_layout.addWidget(self.upload_btn)
        
        # Camera button (placeholder - would need camera integration)
        self.camera_btn = QPushButton("📷 Use Camera")
        self.camera_btn.setMinimumHeight(50)
        self.camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a6bc4;
            }
        """)
        self.camera_btn.clicked.connect(self.use_camera)
        button_layout.addWidget(self.camera_btn)
        
        layout.addLayout(button_layout)
        
        # Analyze button
        self.analyze_btn = QPushButton("🔍 Analyze Product")
        self.analyze_btn.setMinimumHeight(60)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_image)
        layout.addWidget(self.analyze_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.progress_label)
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create right results panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Results tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 3px solid #4CAF50;
            }
        """)
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tabs.addTab(self.overview_tab, "📊 Overview")
        
        # Claims tab
        self.claims_tab = self.create_claims_tab()
        self.tabs.addTab(self.claims_tab, "📝 Claims Analysis")
        
        # Certifications tab
        self.certs_tab = self.create_certifications_tab()
        self.tabs.addTab(self.certs_tab, "✓ Certifications")
        
        # Visual analysis tab
        self.visual_tab = self.create_visual_tab()
        self.tabs.addTab(self.visual_tab, "🎨 Visual Analysis")
        
        # Raw data tab
        self.raw_tab = self.create_raw_data_tab()
        self.tabs.addTab(self.raw_tab, "💾 Raw Data")
        
        layout.addWidget(self.tabs)
        
        # Export button
        self.export_btn = QPushButton("💾 Export Report")
        self.export_btn.setEnabled(False)
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        self.export_btn.clicked.connect(self.export_report)
        layout.addWidget(self.export_btn)
        
        return panel
    
    def create_overview_tab(self) -> QWidget:
        """Create overview results tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Score display
        self.score_label = QLabel("Awaiting analysis...")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            padding: 30px;
            background: #f8f8f8;
            border-radius: 10px;
            margin: 20px;
        """)
        content_layout.addWidget(self.score_label)
        
        # Severity indicator
        self.severity_label = QLabel("")
        self.severity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.severity_label.setStyleSheet("font-size: 20px; padding: 10px;")
        content_layout.addWidget(self.severity_label)
        
        # Deception type
        self.deception_label = QLabel("")
        self.deception_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.deception_label.setStyleSheet("font-size: 16px; color: #666; padding: 10px;")
        content_layout.addWidget(self.deception_label)
        
        # Component scores
        scores_group = QGroupBox("Component Scores")
        scores_layout = QGridLayout(scores_group)
        
        self.nlp_score_label = QLabel("NLP: --")
        self.cert_score_label = QLabel("Certification: --")
        self.visual_score_label = QLabel("Visual: --")
        self.kg_score_label = QLabel("Knowledge Graph: --")
        
        for i, label in enumerate([self.nlp_score_label, self.cert_score_label, 
                                   self.visual_score_label, self.kg_score_label]):
            label.setStyleSheet("font-size: 14px; padding: 5px;")
            scores_layout.addWidget(label, i // 2, i % 2)
        
        content_layout.addWidget(scores_group)
        
        # Recommendations
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setMaximumHeight(200)
        self.recommendations_text.setStyleSheet("""
            QTextEdit {
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        content_layout.addWidget(QLabel("📋 Recommendations:"))
        content_layout.addWidget(self.recommendations_text)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_claims_tab(self) -> QWidget:
        """Create claims analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.claims_text = QTextEdit()
        self.claims_text.setReadOnly(True)
        self.claims_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.claims_text)
        
        return tab
    
    def create_certifications_tab(self) -> QWidget:
        """Create certifications tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.certs_text = QTextEdit()
        self.certs_text.setReadOnly(True)
        self.certs_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.certs_text)
        
        return tab
    
    def create_visual_tab(self) -> QWidget:
        """Create visual analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.visual_text = QTextEdit()
        self.visual_text.setReadOnly(True)
        self.visual_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.visual_text)
        
        return tab
    
    def create_raw_data_tab(self) -> QWidget:
        """Create raw data tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setStyleSheet("""
            QTextEdit {
                background: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.raw_text)
        
        return tab
    
    def init_detector(self):
        """Initialize the detector (may take time)"""
        if SustainabilityDetector is None:
            self.statusBar().showMessage("Error: Detector module not found")
            return
        
        self.statusBar().showMessage("Initializing AI models... Please wait...")
        QApplication.processEvents()
        
        try:
            self.detector = SustainabilityDetector()
            self.statusBar().showMessage("Ready - Upload an image to begin")
        except Exception as e:
            self.statusBar().showMessage(f"Error initializing detector: {str(e)}")
    
    def upload_image(self):
        """Handle image upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Product Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def use_camera(self):
        """Handle camera capture (placeholder)"""
        self.statusBar().showMessage("Camera feature coming soon!")
        # Would implement camera capture here
    
    def load_image(self, file_path: str):
        """Load and display image"""
        self.current_image_path = file_path
        
        # Display image
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(
            400, 400,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        # Enable analyze button
        self.analyze_btn.setEnabled(True)
        
        self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
    
    def analyze_image(self):
        """Run analysis on current image"""
        if not self.current_image_path or not self.detector:
            return
        
        # Disable buttons during analysis
        self.analyze_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.camera_btn.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Starting analysis...")
        
        # Create and start analysis thread
        self.analysis_thread = AnalysisThread(self.detector, self.current_image_path)
        self.analysis_thread.finished.connect(self.on_analysis_complete)
        self.analysis_thread.progress.connect(self.on_analysis_progress)
        self.analysis_thread.error.connect(self.on_analysis_error)
        self.analysis_thread.start()
    
    def on_analysis_progress(self, value: int, message: str):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    def on_analysis_complete(self, report: dict):
        """Handle analysis completion"""
        self.current_report = report
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Re-enable buttons
        self.analyze_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
        self.camera_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        # Display results
        self.display_results(report)
        
        self.statusBar().showMessage("Analysis complete!")
    
    def on_analysis_error(self, error_message: str):
        """Handle analysis error"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        self.analyze_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
        self.camera_btn.setEnabled(True)
        
        self.statusBar().showMessage(f"Error: {error_message}")
    
    def display_results(self, report: dict):
        """Display analysis results in tabs"""
        # Overview tab
        score = report['overall_score']
        severity = report['severity']
        
        self.score_label.setText(f"{score:.1f} / 100")
        
        # Color code by severity
        if severity == "Trustworthy":
            color = "#4CAF50"
            emoji = "✓"
        elif severity == "Minor Concerns":
            color = "#FFC107"
            emoji = "⚠"
        elif severity == "Moderate Deception":
            color = "#FF9800"
            emoji = "⚠⚠"
        elif severity == "High Deception":
            color = "#F44336"
            emoji = "⛔"
        else:
            color = "#B71C1C"
            emoji = "⛔⛔"
        
        self.score_label.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            padding: 30px;
            background: {color}22;
            color: {color};
            border: 3px solid {color};
            border-radius: 10px;
            margin: 20px;
        """)
        
        self.severity_label.setText(f"{emoji} {severity}")
        self.severity_label.setStyleSheet(f"font-size: 20px; padding: 10px; color: {color};")
        
        deception_type = report['primary_deception_type'].replace('_', ' ').title()
        self.deception_label.setText(f"Primary Type: {deception_type}")
        
        # Component scores
        comp_scores = report['component_scores']
        self.nlp_score_label.setText(f"NLP: {comp_scores['nlp_analysis']:.1f}")
        self.cert_score_label.setText(f"Certification: {comp_scores['certification_verification']:.1f}")
        self.visual_score_label.setText(f"Visual: {comp_scores['visual_analysis']:.1f}")
        self.kg_score_label.setText(f"Knowledge Graph: {comp_scores['knowledge_graph']:.1f}")
        
        # Recommendations
        recommendations_text = "\n".join(report['recommendations'])
        self.recommendations_text.setText(recommendations_text)
        
        # Claims tab
        claims_html = self.format_claims(report['claims_analysis'])
        self.claims_text.setHtml(claims_html)
        
        # Certifications tab
        certs_html = self.format_certifications(report['certifications'])
        self.certs_text.setHtml(certs_html)
        
        # Visual tab
        visual_html = self.format_visual_analysis(report['visual_indicators'])
        self.visual_text.setHtml(visual_html)
        
        # Raw data tab
        self.raw_text.setText(json.dumps(report, indent=2))
    
    def format_claims(self, claims: list) -> str:
        """Format claims for display"""
        if not claims:
            return "<p>No claims detected.</p>"
        
        html = "<h3>Detected Claims:</h3>"
        
        for i, claim in enumerate(claims, 1):
            credibility = claim.get('credibility', {})
            score = credibility.get('score', 0)
            
            color = "#4CAF50" if score > 0.7 else "#FFC107" if score > 0.4 else "#F44336"
            
            html += f"""
            <div style='margin: 15px 0; padding: 10px; border-left: 4px solid {color}; background: #f9f9f9;'>
                <p style='margin: 0; font-weight: bold;'>Claim {i}: {claim.get('text', '')}</p>
                <p style='margin: 5px 0; font-size: 12px;'>
                    Type: {claim.get('type', 'unknown')} | 
                    Credibility: {score:.2f} | 
                    Vagueness: {claim.get('vagueness_score', 0):.2f}
                </p>
                {f"<p style='margin: 5px 0; color: red;'>Issues: {', '.join(credibility.get('issues', []))}</p>" if credibility.get('issues') else ""}
            </div>
            """
        
        return html
    
    def format_certifications(self, certs: dict) -> str:
        """Format certifications for display"""
        html = "<h3>Certification Analysis:</h3>"
        
        verified = certs.get('verified', [])
        
        if not verified:
            return html + "<p>No certifications detected.</p>"
        
        for cert in verified:
            is_verified = cert.get('verified')
            is_trustworthy = cert.get('trustworthy', True)
            
            if is_verified == True:
                color = "#4CAF50"
                icon = "✓"
                status = "Verified"
            elif is_verified == 'partial':
                color = "#FFC107"
                icon = "⚠"
                status = "Partially Verified"
            elif not is_trustworthy:
                color = "#F44336"
                icon = "✗"
                status = "Questionable/Fake"
            else:
                color = "#FF9800"
                icon = "?"
                status = "Unverified"
            
            html += f"""
            <div style='margin: 15px 0; padding: 10px; border-left: 4px solid {color}; background: #f9f9f9;'>
                <p style='margin: 0; font-weight: bold;'>{icon} {cert.get('name', 'Unknown')}</p>
                <p style='margin: 5px 0; font-size: 12px;'>
                    Issuer: {cert.get('issuer', 'N/A')} | Status: {status}
                </p>
                {f"<p style='margin: 5px 0; color: red;'>{cert.get('warning', '')}</p>" if cert.get('warning') else ""}
            </div>
            """
        
        return html
    
    def format_visual_analysis(self, visual: dict) -> str:
        """Format visual analysis for display"""
        html = "<h3>Visual Analysis:</h3>"
        
        html += f"""
        <p><strong>Green Percentage:</strong> {visual.get('green_percentage', 0):.1f}%</p>
        <p><strong>Excessive Green:</strong> {'Yes ⚠' if visual.get('excessive_green') else 'No ✓'}</p>
        <p><strong>Nature Imagery:</strong> {'Yes ⚠' if visual.get('nature_imagery') else 'No ✓'}</p>
        <p><strong>Visual Deception Score:</strong> {visual.get('visual_deception_score', 0):.2f}</p>
        """
        
        return html
    
    def export_report(self):
        """Export report to JSON file"""
        if not self.current_report:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            f"sustainability_report_{Path(self.current_image_path).stem}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.current_report, f, indent=2)
                self.statusBar().showMessage(f"Report exported to {file_path}")
            except Exception as e:
                self.statusBar().showMessage(f"Export failed: {str(e)}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = SustainabilityDetectorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
