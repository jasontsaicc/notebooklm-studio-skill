# Output Contracts

## Report contract (markdown)
- Title
- Context (2-3 lines)
- Key architecture/process points
- Risks / limitations
- Action items

## Quiz contract (JSON)
- Array of 5-10 multiple-choice questions
- Each item:
  - `question`
  - `choices` (>=4)
  - `answer`
  - `explanation`

## Flashcards contract (JSON)
- Array of 8-20 cards
- Each item:
  - `front`
  - `back`
  - `tags` (optional)

## Mind Map contract (JSON)
- Tree structure with:
  - `label`: node text
  - `children`: array of child nodes (recursive)
- Root node represents the main topic
- Max depth: 4 levels

## Slides contract
- Downloaded file (PDF or PPTX)
- If generation fails: provide error summary

## Podcast contract
- If success: provide audio artifact path/url + duration
- If fail: provide error summary + retry count + fallback decision

## Delivery status contract
Provide a compact table/list:
- report: success|fail (+ path)
- quiz: success|fail (+ path)
- flashcards: success|fail (+ path)
- mindmap: success|fail (+ path)
- slides: success|fail (+ path)
- podcast: success|fail (+ path or reason)
