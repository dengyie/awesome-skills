import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ZeroToWebsiteDesignPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "intake-brief.md",
            ROOT / "references" / "concept-generation.md",
            ROOT / "references" / "visual-provenance.md",
            ROOT / "references" / "design-system-docs.md",
            ROOT / "references" / "design-rounds.md",
            ROOT / "references" / "implementation-map.md",
            ROOT / "references" / "route-acceptance.md",
            ROOT / "references" / "visual-qa-checklist.md",
            ROOT / "references" / "design-fidelity-loop.md",
            ROOT / "references" / "historical-mock-pass.md",
            ROOT / "references" / "framework-first-delivery.md",
            ROOT / "references" / "project-memory-integration.md",
            ROOT / "references" / "production-delivery.md",
            ROOT / "assets" / "templates" / "design-system-master.md",
            ROOT / "assets" / "templates" / "implementation-plan.md",
            ROOT / "assets" / "templates" / "asset-and-data-spec.md",
            ROOT / "assets" / "templates" / "page-spec.md",
            ROOT / "assets" / "templates" / "visual-source-map.md",
            ROOT / "assets" / "templates" / "visual-source-inventory.md",
            ROOT / "assets" / "templates" / "mock-asset-pass.md",
            ROOT / "assets" / "templates" / "website-workstream.md",
            ROOT / "assets" / "templates" / "qa-report.md",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: zero-to-website-design", frontmatter)
        self.assertIn("complete website", frontmatter)
        self.assertIn("reference images", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Zero-To-Website Design"', metadata)
        self.assertIn("short_description:", metadata)
        self.assertIn("website", metadata.lower())
        self.assertIn("$zero-to-website-design", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertGreaterEqual(len(reference_paths), 9)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]

        self.assertEqual(missing, [])

    def test_templates_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        template_paths = sorted(set(re.findall(r"`(assets/templates/[^`]+\.md)`", skill_text)))

        self.assertEqual(len(template_paths), 9)
        missing = [path for path in template_paths if not (ROOT / path).exists()]

        self.assertEqual(missing, [])

    def test_usage_workflow_summary_matches_skill_workflow_count(self):
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("The skill guides Codex through 13 gates:", usage_text)
        self.assertIn("1. Restore project context and define the website milestone.", usage_text)
        self.assertIn("8. Run the design fidelity setup for binding references.", usage_text)
        self.assertIn("13. Integrate project memory when the work is long-running.", usage_text)
        self.assertNotIn("eleven gates", usage_text)

    def test_skill_and_usage_docs_require_milestone_driven_delivery(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "define the website milestone",
            "P0",
            "P1",
            "P2/P3",
            "Manual-required",
            "phase limit",
            "phase-gate review",
            "Do not start a new milestone automatically",
        ]:
            self.assertIn(expected, skill_text)

        self.assertIn("Milestone-Driven Delivery", usage_text)
        self.assertIn("finite milestone contract", usage_text)
        self.assertIn("workflow stops instead of automatically starting another milestone", usage_text)

    def test_design_rounds_are_required_before_broad_implementation(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        design_rounds = (ROOT / "references" / "design-rounds.md").read_text(
            encoding="utf-8"
        )
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )
        implementation_plan_template = (
            ROOT / "assets" / "templates" / "implementation-plan.md"
        ).read_text(encoding="utf-8")
        qa_report_template = (ROOT / "assets" / "templates" / "qa-report.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "design-rounds.md",
            "design rounds are workflow gates inside the current milestone",
            "Do not collapse the rounds into a single final checklist",
            "Round 1 visual direction selection",
            "Round 4 implementation slice",
        ]:
            self.assertIn(expected, skill_text)

        for expected in [
            "Round 0: Context And Milestone",
            "Round 1: Visual Direction Candidates",
            "Round 2: Design System And Route Decomposition",
            "Round 3: Implementation Map And Asset Plan",
            "Round 4: Implementation Slice",
            "Round 5: Page Item Fidelity Fix Loop",
            "Round 6: Final Delivery Gate",
            "Required Output",
            "Entry Criteria",
            "Exit Criteria",
            "User Confirmation",
            "No-Skip Rules",
            "Do not start broad implementation before Round 3 exits",
            "Do not claim `Visual Delivery Ready` when any required round is skipped",
        ]:
            self.assertIn(expected, design_rounds)

        self.assertIn("Design Rounds", usage_text)
        self.assertIn("do not collapse rounds into one pass", usage_text)
        self.assertIn("Round 1 requires user selection", usage_text)
        self.assertIn("## Design Round State", implementation_plan_template)
        self.assertIn("Current round", implementation_plan_template)
        self.assertIn("Round exit evidence", implementation_plan_template)
        self.assertIn("## Design Round Evidence", qa_report_template)
        self.assertIn("Skipped or collapsed required rounds block final delivery", qa_report_template)

    def test_design_reference_fidelity_loop_is_required(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )
        fidelity = (ROOT / "references" / "design-fidelity-loop.md").read_text(
            encoding="utf-8"
        )
        visual_qa = (ROOT / "references" / "visual-qa-checklist.md").read_text(
            encoding="utf-8"
        )
        implementation_map = (ROOT / "references" / "implementation-map.md").read_text(
            encoding="utf-8"
        )
        qa_report_template = (ROOT / "assets" / "templates" / "qa-report.md").read_text(
            encoding="utf-8"
        )
        implementation_plan_template = (
            ROOT / "assets" / "templates" / "implementation-plan.md"
        ).read_text(encoding="utf-8")

        for expected in [
            "design-fidelity-loop.md",
            "reference decomposition",
            "fidelity pass",
            "implementation screenshot",
            "deviation backlog",
            "asset prompt",
        ]:
            self.assertIn(expected, skill_text)

        self.assertIn("Reference Fidelity", usage_text)
        self.assertIn("design screenshot", usage_text)
        self.assertIn("side-by-side", usage_text)

        for expected in [
            "Reference Decomposition",
            "Page Item Fidelity Audit",
            "itemized comparison table",
            "Fidelity Budget",
            "UI Asset And Component Prompting",
            "Use image generation when a design needs bespoke UI imagery",
            "Prompt Template",
            "Implementation Screenshot Loop",
            "Side-by-side comparison",
            "difference summary",
            "Any `not-checked` required item blocks `Visual Delivery Ready`",
            "no required page item remains `not-checked` or `blocked`",
            "Fix Loop",
            "Final Acceptance",
            "Do not claim visual parity",
        ]:
            self.assertIn(expected, fidelity)

        for expected in [
            "reference screenshot path",
            "implementation screenshot path",
            "side-by-side comparison path",
            "page item fidelity audit path",
            "fidelity status",
            "blocking visual deviations",
            "unchecked design items",
            "blocked design items",
        ]:
            self.assertIn(expected, visual_qa)

        for expected in [
            "Reference decomposition",
            "Fidelity budget",
            "Generated UI asset prompts",
            "Screenshot comparison destination",
        ]:
            self.assertIn(expected, implementation_map)

        self.assertIn("## Reference Fidelity", qa_report_template)
        self.assertIn("Side-by-side comparison", qa_report_template)
        self.assertIn("## Page Item Fidelity Audit", qa_report_template)
        self.assertIn("Design Item", qa_report_template)
        self.assertIn("Reference Region", qa_report_template)
        self.assertIn("Implementation Region", qa_report_template)
        self.assertIn("Evidence Quality", qa_report_template)
        self.assertIn("Match Status", qa_report_template)
        self.assertIn("Unresolved `not-checked` or `blocked` items prevent visual delivery signoff", qa_report_template)
        self.assertIn("Rows with `weak` evidence quality do not support visual delivery signoff", qa_report_template)
        self.assertIn("Blocking visual deviations", qa_report_template)
        self.assertIn("Reference Fidelity Plan", implementation_plan_template)
        self.assertIn("Generated UI asset prompts", implementation_plan_template)

    def test_visual_delivery_closure_gates_are_required(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        fidelity = (ROOT / "references" / "design-fidelity-loop.md").read_text(
            encoding="utf-8"
        )
        visual_qa = (ROOT / "references" / "visual-qa-checklist.md").read_text(
            encoding="utf-8"
        )
        production_delivery = (ROOT / "references" / "production-delivery.md").read_text(
            encoding="utf-8"
        )
        implementation_plan_template = (
            ROOT / "assets" / "templates" / "implementation-plan.md"
        ).read_text(encoding="utf-8")
        qa_report_template = (ROOT / "assets" / "templates" / "qa-report.md").read_text(
            encoding="utf-8"
        )
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "do not implement a final visual pass before the user has seen and selected a concrete image",
            "Create a Reference-To-DOM Map before implementation",
            "No visible region may remain `visual memory only`",
            "component slot first",
            "top 3 visible differences",
            "visual usability gate",
            "not mojibake",
            "first-viewport composition",
            "Treat user visual feedback as status input",
            "final visual pass report",
        ]:
            self.assertIn(expected, skill_text)

        for expected in [
            "Reference-To-DOM Map",
            "Reference Region | DOM Component | Text Real DOM? | Asset Strategy | Interaction | Must Not Do",
            "No region may remain `visual memory only`",
            "Component-Slot Raster Asset Rules",
            "Allowed component-slot raster assets",
            "Disallowed runtime raster shortcuts",
            "full-viewport background mockups",
            "sliced screenshots that carry layout, readable text, navigation, or core controls",
            "Target component size/aspect ratio",
            "Perspective/tilt ownership",
            "top 3 visible differences before the next edit pass",
            "User Feedback Status Updates",
            "blocked-visual",
            "Visual Usability Gate",
            "text is readable and not mojibake",
            "first-viewport composition follows the reference",
        ]:
            self.assertIn(expected, fidelity)

        for expected in [
            "top 3 visible differences after the latest visual pass",
            "Reference-To-DOM Map path",
            "Missing Reference-To-DOM mapping is a blocking visual deviation",
            "Mojibake or unreadable text is a blocking visual and content failure",
            "Visual Usability Gate",
            "first viewport composition matches reference",
        ]:
            self.assertIn(expected, visual_qa)

        for expected in [
            "Final Visual Pass Report",
            "Runtime guards",
            "no full reference image",
            "real DOM links/text",
            "text encoding",
            "Top 3 latest visual differences",
            "Do not claim `Visual Delivery Ready` when the implementation only shares palette or mood",
            "the user has not seen the latest screenshot",
        ]:
            self.assertIn(expected, production_delivery)

        for expected in [
            "Reference-To-DOM Map",
            "Component-Slot Asset Records",
            "Target Size Or Aspect Ratio",
            "Perspective/Tilt Ownership",
            "Top 3 visible differences record",
        ]:
            self.assertIn(expected, implementation_plan_template)

        for expected in [
            "Top 3 Visible Differences",
            "Reference-To-DOM Map Check",
            "Component-Slot Asset Records",
            "Text is readable and not mojibake",
            "Visual Usability Gate",
            "Final Visual Pass Report",
        ]:
            self.assertIn(expected, qa_report_template)

        for expected in [
            "a written style direction is not enough for `Visual Delivery Ready`",
            "Reference-To-DOM Map",
            "top 3 visible differences after every visual pass",
            "Component-slot raster assets are allowed",
            "text readable with no mojibake",
            "User visual feedback updates route status",
        ]:
            self.assertIn(expected, usage_text)

    def test_binding_routes_require_page_item_fidelity_audit(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        fidelity = (ROOT / "references" / "design-fidelity-loop.md").read_text(
            encoding="utf-8"
        )
        route_acceptance = (ROOT / "references" / "route-acceptance.md").read_text(
            encoding="utf-8"
        )
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "page-by-page, item-by-item fidelity audit",
            "Compare each route's hero, navigation, sections, cards, typography blocks, asset slots, decorative resources, spacing, and responsive states",
            "unchecked design items",
            "unresolved blocking item mismatches",
        ]:
            self.assertIn(expected, skill_text)

        for expected in [
            "Required item categories",
            "Verifiable Evidence Rules",
            "reference screenshot path",
            "implementation screenshot path",
            "reference region, crop path, coordinate range",
            "implementation region, crop path, coordinate range",
            "evidence quality: `specific`, `annotated`, `cropped`, or `weak`",
            "Rows marked `weak` cannot support `Visual Delivery Ready`",
            "fresh recheck evidence after the fix",
            "route canvas, viewport, background, and page bounds",
            "header, navigation, logo, and primary actions",
            "hero composition",
            "every visible section in order",
            "repeated components such as cards",
            "typography blocks",
            "illustrations, product shots, icons, ornaments, textures",
            "responsive/mobile ordering",
            "A route with only a high-level screenshot comparison but no itemized audit blocks `Visual Delivery Ready`",
            "vague evidence such as \"looks close\"",
        ]:
            self.assertIn(expected, fidelity)

        self.assertIn("Item Audit", route_acceptance)
        self.assertIn("Every binding design item for the route and required viewport is audited", route_acceptance)
        self.assertIn("blocked item-level mismatches", route_acceptance)
        self.assertIn("item-by-item fidelity audit", usage_text)
        self.assertIn("Any unchecked or blocked required item prevents `Visual Delivery Ready`", usage_text)
        self.assertIn("Each audit row must be independently verifiable", usage_text)
        self.assertIn("Vague evidence such as \"looks close\" or \"see screenshot\" is treated as not checked", usage_text)

    def test_palette_only_reference_copy_is_explicitly_forbidden(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        fidelity = (ROOT / "references" / "design-fidelity-loop.md").read_text(
            encoding="utf-8"
        )
        visual_qa = (ROOT / "references" / "visual-qa-checklist.md").read_text(
            encoding="utf-8"
        )
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "Do not treat a reference image as a palette",
            "Palette-only restyling is a blocking failure",
            "just recolored the page",
            "component silhouette",
            "draw or generate the missing UI assets",
            "reference-image failure mode",
        ]:
            self.assertIn(expected, fidelity)

        self.assertIn("Do not treat binding references as mood boards or palettes", skill_text)
        self.assertIn("Palette-only restyling is a blocking visual deviation", visual_qa)
        self.assertIn("Palette-only restyling is not a fidelity pass", usage_text)

    def test_binding_reference_cannot_be_shipped_as_full_page_screenshot(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        fidelity = (ROOT / "references" / "design-fidelity-loop.md").read_text(
            encoding="utf-8"
        )
        visual_qa = (ROOT / "references" / "visual-qa-checklist.md").read_text(
            encoding="utf-8"
        )
        route_acceptance = (ROOT / "references" / "route-acceptance.md").read_text(
            encoding="utf-8"
        )
        qa_report_template = (ROOT / "assets" / "templates" / "qa-report.md").read_text(
            encoding="utf-8"
        )
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "Do not ship a binding reference as a full-page screenshot",
            "transparent hotspots",
            "real DOM, components, text, controls, charts, links, and responsive behavior",
            "Screenshot-as-page implementation is a blocking failure",
            "reference screenshot may be used for QA evidence",
        ]:
            self.assertIn(expected, fidelity)

        for expected in [
            "Do not satisfy a binding route by placing the whole reference screenshot on the page",
            "Rebuild the selected image as real DOM, components, local assets, and interactions",
        ]:
            self.assertIn(expected, skill_text)

        self.assertIn("Full-page screenshot implementation is a blocking visual deviation", visual_qa)
        self.assertIn("full-page screenshot implementation", route_acceptance)
        self.assertIn("Full-page screenshot implementation check", qa_report_template)
        self.assertIn("Do not ship the selected design image as the webpage", usage_text)
        self.assertIn("Transparent hotspots over a screenshot do not count as implemented interactions", usage_text)

    def test_from_zero_sites_require_user_selected_visual_direction_gate(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        concept_generation = (ROOT / "references" / "concept-generation.md").read_text(
            encoding="utf-8"
        )
        provenance = (ROOT / "references" / "visual-provenance.md").read_text(
            encoding="utf-8"
        )
        production_delivery = (ROOT / "references" / "production-delivery.md").read_text(
            encoding="utf-8"
        )
        framework_delivery = (ROOT / "references" / "framework-first-delivery.md").read_text(
            encoding="utf-8"
        )
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "Treat the user's visual direction choice as a material decision",
            "create 2-4 candidate visual directions or homepage mockups",
            "wait for the user to choose or combine a direction before visual implementation",
            "Without user-selected visual authority, the milestone can only target `Framework Ready`",
            "A text description alone is not `approved-direction`",
            "from-zero or visually open work has either a user-selected visual direction recorded",
        ]:
            self.assertIn(expected, skill_text)

        for expected in [
            "User-Selected Visual Direction Gate",
            "2-4 candidate direction images, homepage mockups, or route mockups",
            "Do not treat a text-only style phrase",
            "do not skip user selection for from-zero visual direction work",
            "do not claim `Visual Delivery Ready` from unselected concept images",
        ]:
            self.assertIn(expected, concept_generation)

        self.assertIn("A text-only direction, agent preference, or assumed mood cannot become `binding-route`", provenance)
        self.assertIn("no route may be marked `Visual Delivery Ready`", provenance)
        self.assertIn("without a user-selected visual direction can only be reported as `Framework Ready`", production_delivery)
        self.assertIn("from-zero visual direction has been selected by the user", framework_delivery)
        self.assertIn("User-selected visual direction is a hard gate", usage_text)

    def test_visual_provenance_contract_names_statuses_and_sources(self):
        provenance = (ROOT / "references" / "visual-provenance.md").read_text(
            encoding="utf-8"
        )

        for status in [
            "exploratory",
            "candidate",
            "approved-direction",
            "binding-route",
            "temporary-binding",
            "obsolete",
        ]:
            self.assertIn(f"`{status}`", provenance)

        for source_method in [
            "user-upload",
            "imagegen",
            "figma-export",
            "live-screenshot",
            "manual-design",
            "existing-project-mockup",
            "existing-project-screenshot",
            "other",
        ]:
            self.assertIn(f"`{source_method}`", provenance)

        for expected in [
            "Authority Reason",
            "Milestone Supported",
            "Replacement Trigger",
            "whole route composition",
            "section composition",
            "illustration slot shape",
            "palette or texture only",
            "`Framework Ready`",
            "`Visual Delivery Ready`",
        ]:
            self.assertIn(expected, provenance)

    def test_skill_and_usage_docs_include_historical_mock_and_framework_ready_language(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )
        historical_mock = (ROOT / "references" / "historical-mock-pass.md").read_text(
            encoding="utf-8"
        )
        framework_delivery = (ROOT / "references" / "framework-first-delivery.md").read_text(
            encoding="utf-8"
        )
        implementation_map = (ROOT / "references" / "implementation-map.md").read_text(
            encoding="utf-8"
        )
        production_delivery = (ROOT / "references" / "production-delivery.md").read_text(
            encoding="utf-8"
        )
        route_acceptance = (ROOT / "references" / "route-acceptance.md").read_text(
            encoding="utf-8"
        )
        visual_qa = (ROOT / "references" / "visual-qa-checklist.md").read_text(
            encoding="utf-8"
        )
        memory_integration = (ROOT / "references" / "project-memory-integration.md").read_text(
            encoding="utf-8"
        )
        visual_source_template = (ROOT / "assets" / "templates" / "visual-source-map.md").read_text(
            encoding="utf-8"
        )
        implementation_plan_template = (
            ROOT / "assets" / "templates" / "implementation-plan.md"
        ).read_text(encoding="utf-8")
        page_spec_template = (ROOT / "assets" / "templates" / "page-spec.md").read_text(
            encoding="utf-8"
        )
        asset_data_template = (
            ROOT / "assets" / "templates" / "asset-and-data-spec.md"
        ).read_text(encoding="utf-8")
        design_system_template = (
            ROOT / "assets" / "templates" / "design-system-master.md"
        ).read_text(encoding="utf-8")
        concept_generation = (ROOT / "references" / "concept-generation.md").read_text(
            encoding="utf-8"
        )
        mock_asset_template = (ROOT / "assets" / "templates" / "mock-asset-pass.md").read_text(
            encoding="utf-8"
        )
        qa_report_template = (ROOT / "assets" / "templates" / "qa-report.md").read_text(
            encoding="utf-8"
        )
        visual_inventory_template = (
            ROOT / "assets" / "templates" / "visual-source-inventory.md"
        ).read_text(encoding="utf-8")

        self.assertIn("historical mock", skill_text.lower())
        self.assertIn("framework-first", skill_text.lower())
        self.assertIn("not to generate new images yet", skill_text.lower())
        self.assertIn("project memory", skill_text.lower())
        self.assertIn("Preserve a compact intake output", skill_text)
        self.assertIn("Do not treat design docs as post-hoc cleanup", skill_text)
        self.assertIn("Treat the implementation map as a pre-code gate", skill_text)
        self.assertIn("pre-code document gate", skill_text.lower())
        self.assertIn("Historical-Mock Path", usage_text)
        self.assertIn("Pre-Code Document Gate", usage_text)
        self.assertIn("route inventory, deferred routes, source-path choice, milestone target", usage_text)
        self.assertIn("Do not generate new images yet", usage_text)
        self.assertIn("temporary-binding", usage_text)
        self.assertIn("Project Memory", usage_text)
        self.assertIn("Generated-Authority Path", usage_text)
        self.assertIn("Record why generation was needed", usage_text)
        self.assertIn("route evidence rows", usage_text)
        self.assertIn("not-checked", usage_text)
        self.assertIn("Visual Delivery Ready", usage_text)
        self.assertIn("Keep this output in the project's design docs", (ROOT / "references" / "intake-brief.md").read_text(encoding="utf-8"))
        self.assertIn("intentionally deferred routes or route types", (ROOT / "references" / "intake-brief.md").read_text(encoding="utf-8"))
        self.assertIn("chosen source path for this milestone", (ROOT / "references" / "intake-brief.md").read_text(encoding="utf-8"))
        self.assertIn("Treat these documents as a pre-code gate", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("route inventory and intentionally deferred routes", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("verification destination for route evidence", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("Do not use implementation mapping as retroactive paperwork", implementation_map)
        self.assertIn("## Preconditions", implementation_map)
        self.assertIn("a compact intake output or equivalent assumption record", implementation_map)
        self.assertIn("stated milestone target and route-verification destination", implementation_map)
        self.assertIn("Record intentionally deferred routes or blockers", implementation_map)
        self.assertIn("Intake basis", implementation_map)
        self.assertIn("Deferred routes", implementation_map)
        self.assertIn("Blockers", implementation_map)
        self.assertIn("strong enough for `Framework Ready`", historical_mock)
        self.assertIn("route owner", historical_mock)
        self.assertIn("replacement or upgrade trigger", historical_mock)
        self.assertIn("route composition is accepted", framework_delivery)
        self.assertIn("slot/texture behavior", framework_delivery)
        self.assertIn("route owner", implementation_map)
        self.assertIn("Upgrade triggers", implementation_map)
        self.assertIn("Framework Ready", route_acceptance)
        self.assertIn("Visual Delivery Ready", route_acceptance)
        self.assertIn("replacement triggers", route_acceptance)
        self.assertIn("Route Evidence Contract", route_acceptance)
        self.assertIn("Viewports Checked", route_acceptance)
        self.assertIn("framework-ready", route_acceptance)
        self.assertIn("visual-delivery-ready", route_acceptance)
        self.assertIn("blocking-framework", route_acceptance)
        self.assertIn("accepted-gap", route_acceptance)
        self.assertIn("Required Evidence Fields", visual_qa)
        self.assertIn("Failure Classification", visual_qa)
        self.assertIn("console result", visual_qa)
        self.assertIn("overflow result", visual_qa)
        self.assertIn("Browser QA must cover both desktop and mobile", visual_qa)
        self.assertIn("workstream", memory_integration.lower())
        self.assertIn("handoff", memory_integration.lower())
        self.assertIn("decisions.md", memory_integration)
        self.assertIn("binding-route", visual_source_template)
        self.assertIn("temporary-binding", visual_source_template)
        self.assertIn("Authority Reason", visual_source_template)
        self.assertIn("Milestone Supported", visual_source_template)
        self.assertIn("Replacement Trigger", visual_source_template)
        self.assertIn("Route composition owners", visual_source_template)
        self.assertIn("Temporary-binding upgrades in flight", visual_source_template)
        self.assertIn("Weakest expected route status", implementation_plan_template)
        self.assertIn("Route Ownership And Risks", implementation_plan_template)
        self.assertIn("Route evidence destination", implementation_plan_template)
        self.assertIn("Accepted-gap policy", implementation_plan_template)
        self.assertIn("Blocking failure rule", implementation_plan_template)
        self.assertIn("## Route Identity", page_spec_template)
        self.assertIn("Source owner", page_spec_template)
        self.assertIn("Viewport evidence target", page_spec_template)
        self.assertIn("Current route status", page_spec_template)
        self.assertIn("## QA Evidence", page_spec_template)
        self.assertIn("Blocking failures", page_spec_template)
        self.assertIn("Accepted gaps", page_spec_template)
        self.assertIn("Source Method", asset_data_template)
        self.assertIn("Authority Status", asset_data_template)
        self.assertIn("Ownership Scope", asset_data_template)
        self.assertIn("Replacement Trigger", asset_data_template)
        self.assertIn("Temporary visual scope", asset_data_template)
        self.assertIn("Replacement triggers are recorded", asset_data_template)
        self.assertIn("## Delivery State", design_system_template)
        self.assertIn("Milestone target", design_system_template)
        self.assertIn("Final route-readiness gate", design_system_template)
        self.assertIn("Binding-route references", design_system_template)
        self.assertIn("Temporary-binding references", design_system_template)
        self.assertIn("Weakest allowed route evidence status", design_system_template)
        self.assertIn("temporary-binding assets say whether they still control route composition", production_delivery)
        self.assertIn("route evidence status for each touched core route", production_delivery)
        self.assertIn("Readiness Claim Rules", production_delivery)
        self.assertIn("weakest required route evidence status", production_delivery)
        self.assertIn("## Route Evidence", qa_report_template)
        self.assertIn("Source Owner", qa_report_template)
        self.assertIn("Blocking Failures", qa_report_template)
        self.assertIn("Accepted Gaps", qa_report_template)
        self.assertIn("Overall route evidence status", qa_report_template)
        self.assertIn("Final readiness claim follows weakest required route evidence status", qa_report_template)
        self.assertIn("Route owner", mock_asset_template)
        self.assertIn("Replacement trigger", mock_asset_template)
        self.assertIn("Authority Reason", visual_inventory_template)
        self.assertIn("Replacement Trigger", visual_inventory_template)
        self.assertIn("Generation Entry Conditions", concept_generation)
        self.assertIn("record why the stronger non-generated source paths were not sufficient", concept_generation)
        self.assertIn("Only move it to `binding-route`", concept_generation)
        self.assertIn("replacement trigger is explicit", concept_generation)
        self.assertIn("do not generate merely because generation is available", concept_generation)

    def test_templates_are_scaffolds_without_todo_markers(self):
        templates_dir = ROOT / "assets" / "templates"
        template_files = sorted(templates_dir.glob("*.md"))

        self.assertEqual(len(template_files), 9)
        for template in template_files:
            text = template.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# "), template.name)
            self.assertNotIn("TODO", text.upper(), template.name)

    def test_website_workstream_template_captures_memory_aware_delivery_fields(self):
        template = (ROOT / "assets" / "templates" / "website-workstream.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "Current milestone",
            "Framework-ready or delivery-ready",
            "Temporary-binding assets",
            "Production review",
            "decisions.md",
            "Another session needed",
        ]:
            self.assertIn(expected, template)


if __name__ == "__main__":
    unittest.main()
