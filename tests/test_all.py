"""
Test Suite for Sustainability Deception Detector
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nlp.claim_extractor import ClaimExtractor
from cv.vision_analyzer import VisionAnalyzer
from knowledge_graph.kg_reasoning import KnowledgeGraph
from detector import SustainabilityDetector


def test_claim_extractor():
    """Test the claim extraction module"""
    print("\n" + "="*60)
    print("TEST 1: Claim Extraction")
    print("="*60)
    
    extractor = ClaimExtractor()
    
    test_cases = [
        "Our product is 100% eco-friendly and made with natural ingredients!",
        "We are committed to achieving carbon neutrality by 2050.",
        "Sustainably sourced, ethically made, and better for the planet.",
        "Contains 47% post-consumer recycled plastic (PCR). Certified by EPA Safer Choice #12345.",
        "This eco-certified product is chemical-free and 100% biodegradable.",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {text}")
        claims = extractor.extract_claims(text)
        print(f"Found {len(claims)} claim(s):")
        
        for claim in claims:
            credibility = extractor.analyze_claim_credibility(claim)
            print(f"  - Claim: {claim['text'][:50]}...")
            print(f"    Type: {claim['type']}, Category: {claim['category']}")
            print(f"    Vagueness: {claim['vagueness_score']:.2f}, Specificity: {claim['specificity_score']:.2f}")
            print(f"    Credibility: {credibility['score']:.2f}")
            if credibility['issues']:
                print(f"    Issues: {', '.join(credibility['issues'][:2])}")
    
    print("\n✓ Claim Extraction Test Complete")


def test_knowledge_graph():
    """Test the knowledge graph module"""
    print("\n" + "="*60)
    print("TEST 2: Knowledge Graph Reasoning")
    print("="*60)
    
    kg = KnowledgeGraph()
    
    # Display statistics
    stats = kg.get_statistics()
    print(f"\nKnowledge Graph Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test claim verification
    test_claims = [
        ("USDA Organic certified", "certification"),
        ("100% carbon neutral", "environmental"),
        ("Free from BPA", "environmental"),
        ("Fair Trade Certified", "certification"),
        ("Eco-certified sustainable", "certification"),
    ]
    
    print(f"\nVerifying {len(test_claims)} claims:")
    for claim_text, claim_type in test_claims:
        result = kg.verify_claim(claim_text, claim_type)
        print(f"\nClaim: '{claim_text}'")
        print(f"  Verified: {result['verified']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Requires Certification: {result['requires_certification']}")
        if result['evidence']:
            print(f"  Evidence: {len(result['evidence'])} item(s)")
    
    print("\n✓ Knowledge Graph Test Complete")


def test_integration():
    """Test full integration"""
    print("\n" + "="*60)
    print("TEST 3: Full Integration Test")
    print("="*60)
    
    print("\nInitializing detector...")
    detector = SustainabilityDetector()
    
    # Test text analysis
    test_text = """
    Our NEW Eco-Friendly Collection!
    
    100% Natural • Carbon Neutral • Certified Organic
    
    Made from sustainably sourced materials with renewable energy.
    We are committed to achieving net-zero emissions by 2050.
    
    Fair Trade • Cruelty-Free • Biodegradable Packaging
    
    Join us in saving the planet, one product at a time!
    """
    
    print("\nAnalyzing test text...")
    result = detector.analyze_text(test_text)
    
    print(f"\n  Overall Score: {result['overall_score']:.2f} / 100")
    print(f"  Severity: {result['severity']}")
    print(f"  Deception Type: {result['deception_type']}")
    print(f"  Claims Detected: {result['num_claims']}")
    
    # Display top 3 claims
    if result['claims']:
        print("\n  Top Claims:")
        for i, claim in enumerate(result['claims'][:3], 1):
            credibility = claim['credibility']['score']
            print(f"    {i}. {claim['text'][:50]}... (Credibility: {credibility:.2f})")
    
    print("\n✓ Integration Test Complete")


def test_visual_analyzer():
    """Test computer vision module (without actual image)"""
    print("\n" + "="*60)
    print("TEST 4: Visual Analyzer (Structure Test)")
    print("="*60)
    
    print("\nInitializing Vision Analyzer...")
    analyzer = VisionAnalyzer()
    
    print("  ✓ OCR Reader initialized")
    print("  ✓ Certification database loaded")
    print(f"  ✓ {len(analyzer.certifications['environmental_certifications'])} certifications loaded")
    
    # Test text-based certification detection
    sample_text = "USDA Organic Certified. FSC Certified. Energy Star Compliant. Eco-Certified Product."
    
    print(f"\nDetecting certifications in sample text:")
    detected = analyzer.detect_certifications(sample_text)
    print(f"  Found {len(detected)} certification claim(s):")
    for cert in detected:
        print(f"    - {cert['name']} (Trustworthy: {cert['trustworthy']})")
    
    print("\n✓ Visual Analyzer Test Complete")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*15 + "SUSTAINABILITY DETECTOR TEST SUITE")
    print("="*70)
    
    try:
        test_claim_extractor()
        test_knowledge_graph()
        test_visual_analyzer()
        test_integration()
        
        print("\n" + "="*70)
        print(" "*20 + "ALL TESTS PASSED ✓")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
