"""
Main Sustainability Deception Detector
Orchestrates NLP, Computer Vision, and Knowledge Graph analysis
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.claim_extractor import ClaimExtractor
from cv.vision_analyzer import VisionAnalyzer
from knowledge_graph.kg_reasoning import KnowledgeGraph


class SustainabilityDetector:
    """
    Main detector class that orchestrates multi-modal analysis
    """
    
    # Deception type thresholds
    THRESHOLDS = {
        'trustworthy': 20,
        'minor_concerns': 40,
        'moderate_deception': 60,
        'high_deception': 80,
        'severe_deception': 100
    }
    
    def __init__(self):
        """Initialize all analysis modules"""
        print("Initializing Sustainability Detector...")
        print("Loading NLP module...")
        self.claim_extractor = ClaimExtractor()
        
        print("Loading Computer Vision module...")
        self.vision_analyzer = VisionAnalyzer()
        
        print("Loading Knowledge Graph...")
        self.knowledge_graph = KnowledgeGraph()
        
        print("Detector ready!")
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Comprehensive analysis of product image
        
        Args:
            image_path: Path to product image
            
        Returns:
            Complete analysis report
        """
        print(f"\nAnalyzing image: {image_path}")
        
        # Computer vision analysis
        print("  - Performing visual analysis...")
        cv_results = self.vision_analyzer.analyze_image(image_path)
        
        if 'error' in cv_results:
            return {
                'error': cv_results['error'],
                'success': False
            }
        
        # Extract text from image
        extracted_text = cv_results['ocr_results']['text']
        print(f"  - Extracted text ({len(extracted_text)} characters)")
        
        # NLP analysis on extracted text
        print("  - Analyzing claims...")
        text_analysis = self.analyze_text(extracted_text) if extracted_text else {
            'claims': [],
            'overall_score': 0,
            'deception_type': 'unknown'
        }
        
        # Combine results
        print("  - Generating final report...")
        combined_report = self._combine_analyses(
            text_analysis=text_analysis,
            cv_results=cv_results,
            image_path=image_path
        )
        
        return combined_report
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for sustainability deception
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis report
        """
        # Extract claims
        claims = self.claim_extractor.extract_claims(text)
        
        # Analyze each claim
        analyzed_claims = []
        for claim in claims:
            # Get credibility analysis
            credibility = self.claim_extractor.analyze_claim_credibility(claim)
            
            # Verify against knowledge graph
            kg_verification = self.knowledge_graph.verify_claim(
                claim['text'], 
                claim['type']
            )
            
            # Combine analysis
            analyzed_claim = {
                **claim,
                'credibility': credibility,
                'kg_verification': kg_verification
            }
            analyzed_claims.append(analyzed_claim)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(analyzed_claims, {})
        
        # Determine deception type
        deception_type = self._determine_deception_type(analyzed_claims, overall_score)
        
        return {
            'text': text,
            'claims': analyzed_claims,
            'num_claims': len(analyzed_claims),
            'overall_score': overall_score,
            'deception_type': deception_type,
            'severity': self._get_severity_level(overall_score)
        }
    
    def _combine_analyses(self, text_analysis: Dict, cv_results: Dict, 
                         image_path: str) -> Dict:
        """
        Combine text and visual analysis into comprehensive report
        """
        # Weight components
        weights = {
            'nlp': 0.40,
            'certification': 0.30,
            'visual': 0.20,
            'kg_verification': 0.10
        }
        
        # Calculate component scores
        nlp_score = text_analysis.get('overall_score', 0)
        
        # Certification score
        cert_score = self._calculate_certification_score(cv_results)
        
        # Visual score
        visual_score = cv_results.get('overall_score', 0.5) * 100
        
        # Knowledge graph verification score
        kg_score = self._calculate_kg_score(text_analysis.get('claims', []))
        
        # Weighted final score
        final_score = (
            nlp_score * weights['nlp'] +
            cert_score * weights['certification'] +
            visual_score * weights['visual'] +
            kg_score * weights['kg_verification']
        )
        
        # Determine primary deception type
        deception_types = self._identify_deception_types(
            text_analysis.get('claims', []),
            cv_results
        )
        
        # Generate detailed report
        report = {
            'success': True,
            'image_path': image_path,
            'timestamp': self._get_timestamp(),
            
            # Overall Assessment
            'overall_score': round(final_score, 2),
            'severity': self._get_severity_level(final_score),
            'primary_deception_type': deception_types['primary'],
            'all_deception_types': deception_types['all'],
            
            # Component Scores
            'component_scores': {
                'nlp_analysis': round(nlp_score, 2),
                'certification_verification': round(cert_score, 2),
                'visual_analysis': round(visual_score, 2),
                'knowledge_graph': round(kg_score, 2)
            },
            
            # Detailed Findings
            'claims_analysis': text_analysis.get('claims', []),
            'num_claims': text_analysis.get('num_claims', 0),
            
            'certifications': {
                'claimed': cv_results.get('certifications_claimed', []),
                'verified': cv_results.get('certifications_verified', []),
                'fake_detected': len([c for c in cv_results.get('certifications_verified', []) 
                                     if not c.get('trustworthy', True)])
            },
            
            'visual_indicators': cv_results.get('visual_greenwashing', {}),
            
            # Specific Issues
            'red_flags': self._compile_red_flags(text_analysis, cv_results),
            'missing_evidence': self._identify_missing_evidence(text_analysis),
            
            # Recommendations
            'recommendations': self._generate_recommendations(final_score, deception_types),
            
            # Raw Data
            'raw_data': {
                'ocr_results': cv_results.get('ocr_results', {}),
                'color_analysis': cv_results.get('color_analysis', {}),
                'label_regions': cv_results.get('label_regions', [])
            }
        }
        
        return report
    
    def _calculate_certification_score(self, cv_results: Dict) -> float:
        """Calculate score based on certification verification (0-100, lower is better)"""
        verified_certs = cv_results.get('certifications_verified', [])
        
        if not verified_certs:
            return 50  # Neutral - no claims made
        
        score = 50  # Start neutral
        
        for cert in verified_certs:
            if cert.get('verified') == True:
                score -= 15  # Verified cert is good (lowers deception score)
            elif cert.get('verified') == 'partial':
                score -= 5  # Partial verification
            elif not cert.get('trustworthy', True):
                score += 30  # Fake certification is very bad
            else:
                score += 10  # Unverified claim
        
        return max(min(score, 100), 0)
    
    def _calculate_kg_score(self, claims: List[Dict]) -> float:
        """Calculate knowledge graph verification score (0-100, lower is better)"""
        if not claims:
            return 50
        
        verified_claims = []
        unverified_claims = []
        contradictions = []
        
        for claim in claims:
            kg_verification = claim.get('kg_verification', {})
            if kg_verification.get('verified'):
                verified_claims.append(claim)
            else:
                unverified_claims.append(claim)
            
            if kg_verification.get('contradictions'):
                contradictions.extend(kg_verification['contradictions'])
        
        # Calculate score
        total_claims = len(claims)
        score = 50
        
        if total_claims > 0:
            verified_ratio = len(verified_claims) / total_claims
            score -= verified_ratio * 30  # Verified claims reduce score
            
            unverified_ratio = len(unverified_claims) / total_claims
            score += unverified_ratio * 20  # Unverified claims increase score
        
        # Contradictions significantly increase score
        score += len(contradictions) * 15
        
        return max(min(score, 100), 0)
    
    def _calculate_overall_score(self, claims: List[Dict], cv_results: Dict) -> float:
        """
        Calculate overall deception score (0-100)
        0 = Trustworthy, 100 = Severe deception
        """
        if not claims:
            return 0
        
        # Base score on claim credibility
        credibility_scores = [c.get('credibility', {}).get('score', 0.5) for c in claims]
        avg_credibility = np.mean(credibility_scores) if credibility_scores else 0.5
        
        # Convert to deception score (inverse of credibility)
        base_score = (1 - avg_credibility) * 100
        
        # Adjust for vagueness
        avg_vagueness = np.mean([c.get('vagueness_score', 0) for c in claims])
        base_score += avg_vagueness * 20
        
        # Adjust for red flags
        total_red_flags = sum(len(c.get('red_flags', [])) for c in claims)
        base_score += total_red_flags * 5
        
        # Adjust for unverified claims
        unverified = sum(1 for c in claims 
                        if not c.get('kg_verification', {}).get('verified'))
        base_score += (unverified / len(claims)) * 15 if claims else 0
        
        return max(min(base_score, 100), 0)
    
    def _determine_deception_type(self, claims: List[Dict], score: float) -> str:
        """Determine the primary type of deception"""
        if not claims:
            return "none"
        
        # Count by type
        type_counts = {}
        for claim in claims:
            claim_type = claim.get('type', 'unknown')
            type_counts[claim_type] = type_counts.get(claim_type, 0) + 1
        
        # Determine primary type
        if not type_counts:
            return "unknown"
        
        primary_type = max(type_counts, key=type_counts.get)
        
        # Map to deception category
        deception_map = {
            'environmental': 'greenwashing',
            'carbon_claim': 'greenwashing',
            'material_claim': 'brownwashing',
            'reduction_claim': 'brownwashing',
            'social': 'bluewashing',
            'labor_claim': 'bluewashing',
            'community_claim': 'bluewashing',
            'certification': 'certification_fraud',
            'temporal': 'temporal_evasion',
            'commitment': 'vague_commitment'
        }
        
        return deception_map.get(primary_type, 'mixed')
    
    def _identify_deception_types(self, claims: List[Dict], 
                                   cv_results: Dict) -> Dict:
        """Identify all types of deception present"""
        types = set()
        
        # From claims
        for claim in claims:
            claim_type = claim.get('type', '')
            category = claim.get('category', '')
            
            if claim_type == 'environmental' or 'carbon' in category:
                types.add('greenwashing')
            if 'material' in category or 'reduction' in category:
                types.add('brownwashing')
            if claim_type == 'social':
                types.add('bluewashing')
            if claim_type == 'certification':
                types.add('certification_fraud')
            if claim.get('vagueness_score', 0) > 0.7:
                types.add('vague_claims')
        
        # From visual analysis
        visual_indicators = cv_results.get('visual_greenwashing', {})
        if visual_indicators.get('excessive_green') or visual_indicators.get('nature_imagery'):
            types.add('visual_greenwashing')
        
        # From certifications
        fake_certs = [c for c in cv_results.get('certifications_verified', []) 
                     if not c.get('trustworthy', True)]
        if fake_certs:
            types.add('fake_certifications')
        
        types_list = list(types)
        return {
            'primary': types_list[0] if types_list else 'none',
            'all': types_list
        }
    
    def _compile_red_flags(self, text_analysis: Dict, cv_results: Dict) -> List[Dict]:
        """Compile all red flags from analysis"""
        red_flags = []
        
        # From claims
        for claim in text_analysis.get('claims', []):
            for flag in claim.get('red_flags', []):
                red_flags.append({
                    'source': 'claim_analysis',
                    'claim': claim.get('text', ''),
                    'flag': flag,
                    'severity': 'high' if 'absolute claim' in flag.lower() else 'medium'
                })
        
        # From certifications
        for cert in cv_results.get('certifications_verified', []):
            if not cert.get('trustworthy', True):
                red_flags.append({
                    'source': 'certification',
                    'flag': f"Questionable certification: {cert.get('name')}",
                    'severity': 'critical'
                })
            elif not cert.get('verified') and cert.get('verified') != 'partial':
                red_flags.append({
                    'source': 'certification',
                    'flag': f"Unverified certification: {cert.get('name')}",
                    'severity': 'high'
                })
        
        # From visual analysis
        visual_indicators = cv_results.get('visual_greenwashing', {})
        if visual_indicators.get('excessive_green'):
            red_flags.append({
                'source': 'visual',
                'flag': f"Excessive green coloring ({visual_indicators.get('green_percentage', 0):.1f}%)",
                'severity': 'medium'
            })
        
        return red_flags
    
    def _identify_missing_evidence(self, text_analysis: Dict) -> List[str]:
        """Identify claims that require but lack evidence"""
        missing = []
        
        for claim in text_analysis.get('claims', []):
            kg_verification = claim.get('kg_verification', {})
            
            if kg_verification.get('requires_certification') and not kg_verification.get('certification_found'):
                missing.append(f"Claim '{claim.get('text')}' requires certification but none provided")
            
            if claim.get('vagueness_score', 0) > 0.7:
                missing.append(f"Claim '{claim.get('text')}' lacks specific, measurable details")
        
        return missing
    
    def _generate_recommendations(self, score: float, deception_types: Dict) -> List[str]:
        """Generate consumer recommendations based on analysis"""
        recommendations = []
        
        if score < 20:
            recommendations.append("✓ This product appears trustworthy with verified environmental claims")
            recommendations.append("✓ Certifications have been verified against legitimate databases")
        elif score < 40:
            recommendations.append("⚠ Minor concerns detected - some claims lack specific details")
            recommendations.append("→ Request additional information from the manufacturer")
        elif score < 60:
            recommendations.append("⚠⚠ Moderate deception indicators present")
            recommendations.append("→ Be skeptical of environmental claims")
            recommendations.append("→ Look for third-party certifications")
        elif score < 80:
            recommendations.append("⛔ High deception risk - multiple red flags")
            recommendations.append("→ Avoid this product if sustainability is important to you")
            recommendations.append("→ Report misleading claims to consumer protection agencies")
        else:
            recommendations.append("⛔⛔ SEVERE DECEPTION DETECTED")
            recommendations.append("→ DO NOT trust environmental claims")
            recommendations.append("→ Report to FTC/consumer protection")
        
        # Type-specific recommendations
        if 'fake_certifications' in deception_types['all']:
            recommendations.append("⚠ Fake or unverifiable certifications detected")
        
        if 'visual_greenwashing' in deception_types['all']:
            recommendations.append("⚠ Visual greenwashing through color/imagery manipulation")
        
        return recommendations
    
    def _get_severity_level(self, score: float) -> str:
        """Convert score to severity category"""
        if score < self.THRESHOLDS['trustworthy']:
            return "Trustworthy"
        elif score < self.THRESHOLDS['minor_concerns']:
            return "Minor Concerns"
        elif score < self.THRESHOLDS['moderate_deception']:
            return "Moderate Deception"
        elif score < self.THRESHOLDS['high_deception']:
            return "High Deception"
        else:
            return "Severe Deception"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_report(self, report: Dict, output_path: str):
        """Export report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report exported to: {output_path}")


if __name__ == "__main__":
    # Test the detector
    detector = SustainabilityDetector()
    
    print("\n" + "="*60)
    print("SUSTAINABILITY DECEPTION DETECTOR - TEST MODE")
    print("="*60)
    
    # Test text analysis
    test_text = """
    Our product is 100% eco-friendly and carbon neutral!
    Made with natural ingredients and certified organic.
    We are committed to achieving sustainability by 2050.
    """
    
    print("\nTesting text analysis:")
    print(f"Text: {test_text.strip()}")
    result = detector.analyze_text(test_text)
    print(f"\nOverall Score: {result['overall_score']:.2f}")
    print(f"Severity: {result['severity']}")
    print(f"Deception Type: {result['deception_type']}")
    print(f"Claims found: {result['num_claims']}")
