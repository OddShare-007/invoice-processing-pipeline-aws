# Documentation and Diagram Design

Use a clean, technical visual language that reads well in a portfolio and remains legible when diagrams are viewed on a laptop or embedded in a README.

## Visual Direction
- **Background:** white or very light neutral gray.
- **Primary text:** charcoal or near-black for strong contrast.
- **AWS services:** restrained AWS orange as the primary accent, with each service labeled clearly.
- **Data movement:** one dark blue or teal accent for arrows and flow direction.
- **Storage and query stages:** muted green or slate accents to distinguish data states without making the diagram busy.
- **Warnings and failures:** amber for recoverable issues and red only for terminal failures.

## Diagram Style
- Use a left-to-right flow: upload, raw storage, processing, processed storage, and querying.
- Use simple rectangles or service icons with short labels; avoid decorative illustrations and excessive shadows.
- Group AWS-managed services within a subtle boundary and show external users or tools outside it.
- Keep arrows directional, consistent, and free of crossings where possible.
- Use one font family, a small type scale, and a concise legend when color has semantic meaning.
- Export diagrams as accessible SVG or high-resolution PNG, and pair each visual with a short text explanation in the README.
