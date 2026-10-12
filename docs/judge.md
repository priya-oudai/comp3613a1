# student-judge competency report

**Judged at:** 2026-10-11T16:32:12-04:00  
**Student / session:** Student Accommodation project; Copilot Agent Guide chats  
**Artifact:** All eight accessible Guide chats saved under `docs/transcripts/`, plus the current report, model sources, diagrams, and wireframes  
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy; never generic 0–5)  
**Evidence pass:** re-read native chats and current project artefacts; no prior scorecard used

### Totals

| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 |
| Metrics scored | 12 |
| Scoreable max | 12 × 4 |
| Awarded total | 44 / 48 |
| **Overall (avg of scored)** | **3.7 / 4** |
| Impression mark | 18 / 20 |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 3 | yes | The student worked through the design phases, completed local polish before deployment, and supplied the live URL. |
| M2 | Problem framing | 4 | yes | “For search and view a property have an extend use case to view listing details … and book a property should have an extend to leave a review.” |
| M3 | Decision ownership | 4 | yes | The student named the workflows and model fields, specified `Confirm Booking` as “separate and independant,” and chose the later review path. |
| M4 | Artefact-before-code | 3 | yes | The report contains the student-named entity model and all three wireframes before the Phase 5 implementation and refinement. |
| M5 | Verification habit | 4 | yes | “yes everything works”; later the student reported concrete role, booking, route, review, and appearance checks and requested further refinements. |
| M6 | Assignment fit | 3 | yes | Implementation notes and code-check evidence show ERD/wireframe-led work, role-aware features, and service/repository use; persistence calls were not found in routers during this evidence pass. |
| M7 | Slice explanation | 4 | yes | The report records model, repository, service, and thin-route snippets; e.g. the student's route “passes query, price band, and type to PropertyService … without persistence logic.” |
| M8 | Prompt quality | 3 | yes | The student used phase-tagged prompts and gave specific mismatch and polish requests, including Search page controls, Cancel Review, review display date, and navigation behavior. |
| M9 | Response to pushback | 4 | yes | The student continued after verification with “there are a couple of things that needs changing” and later confirmed the repaired View Details path worked. |
| M10 | Integrity | 4 | yes | No external-assist/paste-back flags, sincerity spiral, or skill-edit evidence appeared in the accessible chats or current artefacts. |
| M11 | Provenance continuity | 4 | yes | The project, named accommodation workflows, ERD, wireframes, implementation, and later refinements remain consistent across the saved phase chats. |
| M12 | Sincerity trajectory | 4 | yes | No suspicion was raised; therefore no suspicion round was abandoned or left unresolved. |

## Strengths

- Student chose the project and named three user/workflow pairs.
- Student made explicit include/extend and independent-use-case decisions.
- Student named entities and properties, then engaged in relationship and workflow clarification.
- Student supplied wireframes and used them to guide extensive Phase 5 verification and polish.
- Student completed layered code checks; recorded route snippets call services rather than executing persistence logic in routers.
- Student provided a working public Render URL and marker account credentials.

## Gaps (priority order)

None identified from the available evidence.

## Phase gate status

| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Student Accommodation and three named workflows are recorded. |
| 2 | met | Use-case relationships and independent Confirm Booking case are recorded in the UML artefact. |
| 3 | met | Student-named entities/properties and model relationships are present. |
| 4 | met | Three wireframes are embedded with coverage notes; booking/review path was clarified. |
| 5 | met | Theme, workflow implementation, verification, and repeated UI/workflow/model polish are documented. |
| 6 | met | Public Render URL, health-check confirmation, and owner/admin/student marker logins are recorded. |

## Recommended next practice

- Before final submission, use the published marker credentials to verify one student-side flow and one owner-side flow on the live site, using separate browsers or an incognito window as documented.

## Integrity note

- Clean. No external-assist/paste-back or edited-skills evidence was found in the accessible project chats or current artefacts.

## Provenance flags

- None.

## Sincerity log summary

- Blocks found: 0 | max round: none | min/mean/final confidence: N/A | trend: N/A | cleared: not needed

## Skips

- Skips: 1/3 used
- Photo uploads — assumed: use a shared placeholder image rather than collect/store photos.

