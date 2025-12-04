# ResuMAX v2 Architecture

## Core Principle
**LLMs for parsing/reasoning. Deterministic code for layout/formatting.**

## Pipeline Overview

```
PDF Upload
  ↓
[Stage 1] Raw Extraction (No LLM)
  → Extract text with X/Y coordinates, font data, formatting
  → Detect two-column layouts spatially
  → Output: RawDocument with TextBlocks
  ↓
[Stage 2] Structural Segmentation (LLM - Claude Haiku)
  → Identify sections, entries, bullets
  → NO rewriting, NO cleaning
  → Output: StructuredResume JSON
  ↓
[Stage 3] Semantic Cleanup (LLM - GPT-4)
  → Fix broken lines, join fragments
  → Normalize formatting artifacts
  → NO content changes
  ↓
[Stage 4] Validation (LLM check)
  → Compare against raw text
  → Verify nothing missing
  → Fix discrepancies
  ↓
[Stage 5] Canonical JSON
  → Build final resume JSON
  → Single source of truth
  ↓
[Layout Engine] Deterministic Layout
  → Calculate exact positions using font metrics
  → Apply automatic compression (0-4 levels)
  → Guarantee one-page output
  → Output: LayoutResult with positioned elements
  ↓
[Renderer] Generate Preview/PDF
  → Same layout data for both
  → Pixel-perfect consistency
```

## Key Components

### 1. Raw Extractor (`stage1_raw_extraction.py`)
- Uses PyMuPDF to extract text blocks with bounding boxes
- Preserves font name, size, bold, italic
- Detects two-column layouts using horizontal gaps
- NO text cleaning or merging

### 2. Structural Segmenter (`stage2_structural_segmentation.py`)
- LLM (Claude Haiku) identifies structure:
  - Section boundaries
  - Entry boundaries
  - Bullet vs non-bullet text
  - Headers
- Copies text EXACTLY - no rewriting
- Falls back to rule-based if LLM unavailable

### 3. Layout Engine (`layout_engine/`)

#### Font Metrics (`font_metrics.py`)
- Measures exact character widths
- Calculates line breaks with hyphenation
- Measures heights in inches

#### Core Engine (`engine.py`)
- Automatic compression algorithm:
  - Level 0: No compression
  - Level 1: Reduce line-height 1.2 → 1.15
  - Level 2: Tighten spacing
  - Level 3: Reduce bullet indent
  - Level 4: Reduce font size 10pt → 9.5pt
- Iterates until content fits on one page
- Returns positioned elements with exact coordinates

### 4. Layout Result Structure
```python
@dataclass
class LayoutElement:
    element_type: str  # "heading", "text", "bullet"
    text: str
    x: float  # inches from left
    y: float  # inches from top
    width: float
    height: float
    font_size: float
    is_bold: bool
    is_italic: bool
```

## Benefits

### ✅ Fixes Current Issues
1. **Missing project names** - LLM understands structure reliably
2. **Weird spacing** - Layout engine controls all spacing
3. **Orphan words** - Hyphenation + line-width measurement
4. **Whitespace waste** - Compression algorithm is deterministic
5. **Two-column issues** - Raw extractor detects spatially
6. **One-page unreliable** - Engine guarantees it
7. **Preview ≠ PDF** - Both use same layout data

### ✅ User Benefits
- **Predictable** - Same resume always produces same layout
- **Customizable** - Can adjust fonts, sizes, spacing
- **Fast** - LLM only used once during upload
- **Cost-effective** - Haiku for structure, no repeated formatting calls
- **Professional** - Deterministic layout looks polished

## Migration Plan

### Phase 1: Backend (Current)
- [x] Create `parser_v2/` with new pipeline
- [x] Create `layout_engine/` with metrics + engine
- [ ] Integrate with existing upload endpoint
- [ ] Add layout preview API endpoint

### Phase 2: Testing
- [ ] Test Stage 1 raw extraction on sample PDFs
- [ ] Test Stage 2 segmentation with LLM
- [ ] Test layout engine compression
- [ ] Validate with Ryley's resume

### Phase 3: Frontend
- [ ] Create layout preview component (renders LayoutElements)
- [ ] Replace current editor with structured editor
- [ ] Connect to new API endpoints

### Phase 4: Export
- [ ] Build PDF export using ReportLab with LayoutElements
- [ ] Build DOCX export using python-docx
- [ ] Ensure exports match preview exactly

### Phase 5: Optimization
- [ ] Integrate optimization that preserves layout
- [ ] Re-run layout engine after optimization
- [ ] Update preview

## Dependencies

### Already Installed
- `PyMuPDF` (fitz) - PDF extraction
- `openai` - LLM calls
- `fastapi` - API

### Need to Add
- `reportlab` - PDF generation with exact positioning
- `python-docx` - DOCX generation
- `anthropic` (optional) - Claude Haiku API

```bash
pip install reportlab python-docx anthropic
```

## Next Steps

1. Complete remaining pipeline stages (3, 4, 5)
2. Create integration layer connecting all stages
3. Add API endpoint for new pipeline
4. Test with real resumes
5. Build frontend preview renderer
6. Implement PDF/DOCX export
7. Deprecate old parser
