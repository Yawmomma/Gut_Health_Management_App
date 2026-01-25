"""
Script to add histamine education content to the database
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db
from models.education import EducationalContent

def add_histamine_chapter():
    with app.app_context():
        # Check if this chapter already exists
        existing = EducationalContent.query.filter_by(
            chapter_number=2,
            title="Understanding Histamine in Foods"
        ).first()

        if existing:
            print("Histamine chapter already exists. Updating content...")
            chapter = existing
        else:
            print("Creating new histamine education chapter...")
            chapter = EducationalContent()
            chapter.chapter_number = 2
            chapter.order_index = 1
            chapter.section = "Histamine Intolerance"
            chapter.title = "Understanding Histamine in Foods"

        # Set the content
        chapter.content = """
<h2>Understanding Histamine in Foods</h2>

<p class="lead">Histamine is a biogenic amine that serves as a critical signaling molecule, acting as an immune mediator, a neurotransmitter, and a regulator of digestion. In a healthy body, histamine levels are tightly controlled by specific enzymes. When this balance is disrupted by external factors like food, it can lead to "histamine load" or intolerance.</p>

<h3>1. How Histamine Works in the Body</h3>
<p>Histamine functions by binding to four types of receptors (H1–H4) scattered throughout different tissues:</p>

<div class="row mt-3 mb-4">
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title"><i class="bi bi-lungs"></i> H1 Receptors (Immune & Brain)</h5>
                <p class="card-text">Located in the lungs, skin, and blood vessels. They trigger allergic symptoms like itching, hives, and swelling, and help regulate your sleep-wake cycle.</p>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title"><i class="bi bi-heart"></i> H2 Receptors (Stomach & Heart)</h5>
                <p class="card-text">Primarily found in the stomach lining, where they stimulate the production of gastric acid for digestion.</p>
            </div>
        </div>
    </div>
    <div class="col-md-12 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title"><i class="bi bi-brain"></i> H3/H4 Receptors (Nervous System & Gut)</h5>
                <p class="card-text">Involved in regulating neurotransmitter release in the brain and managing inflammatory responses in the gut and bone marrow.</p>
            </div>
        </div>
    </div>
</div>

<h3>2. The Histamine "Bucket" Concept</h3>
<p>Health experts often use the "bucket" metaphor to describe Histamine Load. Your body can handle a certain amount of histamine, but if you "fill the bucket" faster than you can empty it, symptoms appear. The bucket is filled by:</p>

<div class="alert alert-info">
    <ul class="mb-0">
        <li><strong>Endogenous Histamine:</strong> Histamine produced by your own immune cells (mast cells and basophils) in response to triggers.</li>
        <li><strong>Exogenous Histamine:</strong> Histamine ingested directly from food.</li>
    </ul>
</div>

<h3>3. Food-Related Histamine Properties</h3>
<p>Food interacts with your histamine levels in three distinct ways:</p>

<h4>A. Direct Histamine Sources (High-Histamine Foods)</h4>
<div class="card mb-3 border-danger">
    <div class="card-body">
        <p>These are foods where bacteria have already converted the amino acid histidine into histamine.</p>
        <p><strong>Common culprits:</strong> Fermented foods (sauerkraut, kombucha), aged cheeses, cured meats, and canned or smoked fish.</p>
        <p class="mb-0"><strong>Storage effect:</strong> Histamine levels increase over time, meaning leftovers often have higher levels than freshly cooked food.</p>
    </div>
</div>

<h4>B. Histamine Liberators</h4>
<div class="card mb-3 border-warning">
    <div class="card-body">
        <p>These foods may contain very little histamine themselves, but they contain compounds that trigger your mast cells to release their own stored histamine into your system.</p>
        <p class="mb-0"><strong>Examples:</strong> Citrus fruits, strawberries, bananas, chocolate, and certain food additives like carrageenan.</p>
    </div>
</div>

<h4>C. DAO Blockers</h4>
<div class="card mb-3 border-danger">
    <div class="card-body">
        <p>Diamine Oxidase (DAO) is the primary enzyme in your gut that "empties the bucket" by breaking down histamine before it enters your bloodstream. Some substances temporarily disable or "block" this enzyme, allowing histamine levels to spike.</p>
        <p class="mb-0"><strong>Key blockers:</strong> Alcohol (the most potent blocker), caffeinated energy drinks, and certain medications.</p>
    </div>
</div>

<h3>4. Symptoms of Overload</h3>
<p>When histamine accumulation exceeds the body's degradation capacity, it enters the systemic circulation and can cause a "pseudo-allergic" reaction affecting multiple organs:</p>

<div class="row">
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-body">
                <h5><i class="bi bi-stomach"></i> Digestive</h5>
                <p class="mb-0">Bloating, diarrhea, abdominal pain.</p>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-body">
                <h5><i class="bi bi-head-side"></i> Neurological</h5>
                <p class="mb-0">Migraines, headaches, dizziness.</p>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-body">
                <h5><i class="bi bi-droplet"></i> Skin</h5>
                <p class="mb-0">Flushing, hives, unexplained itching.</p>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-body">
                <h5><i class="bi bi-wind"></i> Respiratory</h5>
                <p class="mb-0">Nasal congestion, sneezing, or asthma-like symptoms.</p>
            </div>
        </div>
    </div>
</div>

<h3 class="mt-4">5. Summary: Histamine Regulation</h3>
<div class="table-responsive">
    <table class="table table-bordered">
        <thead class="table-light">
            <tr>
                <th>Component</th>
                <th>Function in Body</th>
                <th>Food/External Impact</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Histamine</strong></td>
                <td>Messenger for immunity & stomach acid.</td>
                <td>Ingested via aged/fermented foods.</td>
            </tr>
            <tr>
                <td><strong>Mast Cells</strong></td>
                <td>Storage "vaults" for your own histamine.</td>
                <td>Triggered by "liberators" like citrus or strawberries.</td>
            </tr>
            <tr>
                <td><strong>DAO Enzyme</strong></td>
                <td>Gut-based "clean-up crew" for food histamine.</td>
                <td>Inhibited by alcohol and certain medications.</td>
            </tr>
            <tr>
                <td><strong>HNMT Enzyme</strong></td>
                <td>Intracellular "clean-up crew" (liver/brain).</td>
                <td>Works on histamine that enters cells.</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="alert alert-success mt-4">
    <h5><i class="bi bi-lightbulb"></i> Key Takeaway</h5>
    <p class="mb-0">Understanding these three food categories (direct sources, liberators, and DAO blockers) is essential for managing histamine intolerance. By tracking your food intake and symptoms in this app, you can identify which foods fill your personal "histamine bucket" too quickly.</p>
</div>
"""

        if not existing:
            db.session.add(chapter)

        db.session.commit()
        print(f"Successfully {'updated' if existing else 'added'} histamine education chapter!")
        print(f"Chapter ID: {chapter.id}")
        print(f"View at: /education/chapter/{chapter.id}")

if __name__ == '__main__':
    add_histamine_chapter()
