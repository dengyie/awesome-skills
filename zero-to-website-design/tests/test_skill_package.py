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
            ROOT / "references" / "implementation-map.md",
            ROOT / "references" / "route-acceptance.md",
            ROOT / "references" / "visual-qa-checklist.md",
            ROOT / "references" / "historical-mock-pass.md",
            ROOT / "references" / "framework-first-delivery.md",
            ROOT / "references" / "content-readiness.md",
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
        self.assertIn("handoff", metadata.lower())
        self.assertIn("route specs", metadata.lower())
        self.assertIn("browser qa", metadata.lower())
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertGreaterEqual(len(reference_paths), 8)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]

        self.assertEqual(missing, [])

    def test_templates_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        template_paths = sorted(set(re.findall(r"`(assets/templates/[^`]+\.md)`", skill_text)))

        self.assertEqual(len(template_paths), 9)
        missing = [path for path in template_paths if not (ROOT / path).exists()]

        self.assertEqual(missing, [])

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
            "Route Family",
            "Readiness Limiter",
            "Upgrade Queue",
            "Next Verification Target",
            "Blocker Owner",
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
        repo_readme = (ROOT.parent / "README.md").read_text(encoding="utf-8")
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
        content_readiness = (ROOT / "references" / "content-readiness.md").read_text(
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
        self.assertIn("active escalation target", skill_text)
        self.assertIn("next verification target", skill_text)
        self.assertIn("Framework-first delivery is valid", skill_text)
        self.assertIn("Preserve a compact intake output", skill_text)
        self.assertIn("Do not treat design docs as post-hoc cleanup", skill_text)
        self.assertIn("Treat the implementation map as a pre-code gate", skill_text)
        self.assertIn("pre-code document gate", skill_text.lower())
        self.assertIn("Delivery Handoff", usage_text)
        self.assertIn("twelve gates", usage_text)
        self.assertIn("temporary-binding or generated-route ownership", usage_text)
        self.assertIn("Framework-ready work can still be valid", usage_text)
        self.assertIn("Historical-Mock Path", usage_text)
        self.assertIn("Pre-Code Document Gate", usage_text)
        self.assertIn("route inventory, deferred routes, source-path choice, milestone target", usage_text)
        self.assertIn("Do not generate new images yet", usage_text)
        self.assertIn("temporary-binding", usage_text)
        self.assertIn("Project Memory", usage_text)
        self.assertIn("Continuity Gate", usage_text)
        self.assertIn("current route slice", usage_text)
        self.assertIn("weakest route evidence status", usage_text)
        self.assertIn("handoff artifact or resume note", usage_text)
        self.assertIn("Content Readiness", usage_text)
        self.assertIn("content source status by route family", usage_text)
        self.assertIn("route-family owner and metadata owner", usage_text)
        self.assertIn("placeholder or draft replacement triggers", usage_text)
        self.assertIn("Route-Data Integrity", usage_text)
        self.assertIn("route-data source of truth", usage_text)
        self.assertIn("feed/output source of truth", usage_text)
        self.assertIn("slug uniqueness and route identity checks", usage_text)
        self.assertIn("Route Specs", usage_text)
        self.assertIn("which data source and metadata source power it", usage_text)
        self.assertIn("what QA evidence belongs to the route", usage_text)
        self.assertIn("what still blocks the route and who owns the unblock", usage_text)
        self.assertIn("Generated-Authority Path", usage_text)
        self.assertIn("Record why generation was needed", usage_text)
        self.assertIn("Generated Route Mockups", usage_text)
        self.assertIn("which routes must be expanded from the chosen concept before coding", usage_text)
        self.assertIn("inherits authority from the selected concept", usage_text)
        self.assertIn("what another session must verify before implementation begins from that mockup", usage_text)
        self.assertIn("Asset Authority Continuity", usage_text)
        self.assertIn("which provisional assets belong to the same upgrade queue", usage_text)
        self.assertIn("what next verification or replacement step another session must run", usage_text)
        self.assertIn("A visual-source note should be enough for another session", usage_text)
        self.assertIn("Delivery Handoff", usage_text)
        self.assertIn("weakest route limiting reason", usage_text)
        self.assertIn("whether generated route mockups still control any route family", usage_text)
        self.assertIn("authority is inherited from a selected concept or is route-specific", usage_text)
        self.assertIn("active escalation target and next verification target", usage_text)
        self.assertIn("route evidence rows", usage_text)
        self.assertIn("not-checked", usage_text)
        self.assertIn("Visual Delivery Ready", usage_text)
        self.assertIn("Keep this output in the project's design docs", (ROOT / "references" / "intake-brief.md").read_text(encoding="utf-8"))
        self.assertIn("intentionally deferred routes or route types", (ROOT / "references" / "intake-brief.md").read_text(encoding="utf-8"))
        self.assertIn("chosen source path for this milestone", (ROOT / "references" / "intake-brief.md").read_text(encoding="utf-8"))
        self.assertIn("Treat these documents as a pre-code gate", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("route inventory and intentionally deferred routes", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("verification destination for route evidence", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("route-data source of truth", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("metadata source of truth", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("route blocker owner when the route is not ready", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("Do not use implementation mapping as retroactive paperwork", implementation_map)
        self.assertIn("## Preconditions", implementation_map)
        self.assertIn("a compact intake output or equivalent assumption record", implementation_map)
        self.assertIn("stated milestone target and route-verification destination", implementation_map)
        self.assertIn("Record intentionally deferred routes or blockers", implementation_map)
        self.assertIn("Intake basis", implementation_map)
        self.assertIn("Deferred routes", implementation_map)
        self.assertIn("Blockers", implementation_map)
        self.assertIn("Route-data source of truth", implementation_map)
        self.assertIn("Metadata source of truth", implementation_map)
        self.assertIn("Feed/export source of truth", implementation_map)
        self.assertIn("Route identity risks", implementation_map)
        self.assertIn("page spec as the route-level source of truth for route-data, metadata, and route-specific blockers", implementation_map)
        self.assertIn("strong enough for `Framework Ready`", historical_mock)
        self.assertIn("route owner", historical_mock)
        self.assertIn("active upgrade queue", historical_mock)
        self.assertIn("readiness limiter", historical_mock)
        self.assertIn("next verification or replacement step", historical_mock)
        self.assertIn("blocker owner", historical_mock)
        self.assertIn("replacement or upgrade trigger", historical_mock)
        self.assertIn("route composition is accepted", framework_delivery)
        self.assertIn("placeholder, curated, or generated-draft content policy is documented", framework_delivery)
        self.assertIn("route-family owner and replacement trigger are named", framework_delivery)
        self.assertIn("which route families still rely on curated, placeholder, or generated-draft content", framework_delivery)
        self.assertIn("slot/texture behavior", framework_delivery)
        self.assertIn("route owner", implementation_map)
        self.assertIn("Upgrade triggers", implementation_map)
        self.assertIn("Framework Ready", route_acceptance)
        self.assertIn("Visual Delivery Ready", route_acceptance)
        self.assertIn("Data/Metadata Integrity", route_acceptance)
        self.assertIn("replacement triggers", route_acceptance)
        self.assertIn("Route Evidence Contract", route_acceptance)
        self.assertIn("Viewports Checked", route_acceptance)
        self.assertIn("framework-ready", route_acceptance)
        self.assertIn("visual-delivery-ready", route_acceptance)
        self.assertIn("blocking-framework", route_acceptance)
        self.assertIn("blocking-data", route_acceptance)
        self.assertIn("Slug collisions, route-data drift, or feed/output mismatches", route_acceptance)
        self.assertIn("accepted-gap", route_acceptance)
        self.assertIn("Required Evidence Fields", visual_qa)
        self.assertIn("Failure Classification", visual_qa)
        self.assertIn("route-data integrity result", visual_qa)
        self.assertIn("metadata integrity result", visual_qa)
        self.assertIn("feed/output integrity result", visual_qa)
        self.assertIn("console result", visual_qa)
        self.assertIn("overflow result", visual_qa)
        self.assertIn("Browser QA must cover both desktop and mobile", visual_qa)
        self.assertIn("workstream", memory_integration.lower())
        self.assertIn("handoff", memory_integration.lower())
        self.assertIn("decisions.md", memory_integration)
        self.assertIn("current route matrix slice", memory_integration)
        self.assertIn("weakest route evidence status", memory_integration)
        self.assertIn("asset upgrade queue", memory_integration)
        self.assertIn("Treat handoff generation as mandatory", memory_integration)
        self.assertIn("Minimum handoff or resume note fields", memory_integration)
        self.assertIn("binding-route", visual_source_template)
        self.assertIn("temporary-binding", visual_source_template)
        self.assertIn("Authority Reason", visual_source_template)
        self.assertIn("Milestone Supported", visual_source_template)
        self.assertIn("Route Family", visual_source_template)
        self.assertIn("Inherited From", visual_source_template)
        self.assertIn("Route-Mockup Coverage", visual_source_template)
        self.assertIn("Escalation Target", visual_source_template)
        self.assertIn("Readiness Limiter", visual_source_template)
        self.assertIn("Upgrade Queue", visual_source_template)
        self.assertIn("Next Verification Target", visual_source_template)
        self.assertIn("Blocker Owner", visual_source_template)
        self.assertIn("Replacement Trigger", visual_source_template)
        self.assertIn("Route composition owners", visual_source_template)
        self.assertIn("Active upgrade queue", visual_source_template)
        self.assertIn("Temporary-binding upgrades in flight", visual_source_template)
        self.assertIn("Next verification target", visual_source_template)
        self.assertIn("Escalation target", visual_source_template)
        self.assertIn("Blocker owner", visual_source_template)
        self.assertIn("content source status by route family", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("placeholder replacement conditions", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("route-family ownership", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("metadata ownership", (ROOT / "references" / "design-system-docs.md").read_text(encoding="utf-8"))
        self.assertIn("Weakest expected route status", implementation_plan_template)
        self.assertIn("Route Ownership And Risks", implementation_plan_template)
        self.assertIn("Route evidence destination", implementation_plan_template)
        self.assertIn("Data source of truth", implementation_plan_template)
        self.assertIn("Metadata source of truth", implementation_plan_template)
        self.assertIn("Feed/export source of truth", implementation_plan_template)
        self.assertIn("Route-data integrity check", implementation_plan_template)
        self.assertIn("Metadata integrity check", implementation_plan_template)
        self.assertIn("Feed/output integrity check", implementation_plan_template)
        self.assertIn("Route identity risk", implementation_plan_template)
        self.assertIn("Mismatch blocker", implementation_plan_template)
        self.assertIn("Accepted-gap policy", implementation_plan_template)
        self.assertIn("Blocking failure rule", implementation_plan_template)
        self.assertIn("## Route Identity", page_spec_template)
        self.assertIn("Source owner", page_spec_template)
        self.assertIn("Route-data source of truth", page_spec_template)
        self.assertIn("Metadata source of truth", page_spec_template)
        self.assertIn("Feed/output relevance", page_spec_template)
        self.assertIn("Viewport evidence target", page_spec_template)
        self.assertIn("Current route status", page_spec_template)
        self.assertIn("## QA Evidence", page_spec_template)
        self.assertIn("Blocking failures", page_spec_template)
        self.assertIn("Accepted gaps", page_spec_template)
        self.assertIn("Route-data and metadata integrity status", page_spec_template)
        self.assertIn("Blocker owner", page_spec_template)
        self.assertIn("Unblock condition", page_spec_template)
        self.assertIn("Route-specific handoff context", page_spec_template)
        self.assertIn("Source Method", asset_data_template)
        self.assertIn("Route Family", asset_data_template)
        self.assertIn("Metadata Owner", asset_data_template)
        self.assertIn("Route families allowed to stay provisional", asset_data_template)
        self.assertIn("Generated-draft content allowed", asset_data_template)
        self.assertIn("Route family owner", asset_data_template)
        self.assertIn("Final delivery blocker", asset_data_template)
        self.assertIn("Framework-ready blocker", asset_data_template)
        self.assertIn("Authority Status", asset_data_template)
        self.assertIn("Ownership Scope", asset_data_template)
        self.assertIn("Replacement Trigger", asset_data_template)
        self.assertIn("Temporary visual scope", asset_data_template)
        self.assertIn("Touched route families have explicit content source status", asset_data_template)
        self.assertIn("Placeholder or generated-draft replacement triggers are recorded", asset_data_template)
        self.assertIn("Replacement triggers are recorded", asset_data_template)
        self.assertIn("## Delivery State", design_system_template)
        self.assertIn("Milestone target", design_system_template)
        self.assertIn("Final route-readiness gate", design_system_template)
        self.assertIn("Binding-route references", design_system_template)
        self.assertIn("Temporary-binding references", design_system_template)
        self.assertIn("Weakest allowed route evidence status", design_system_template)
        self.assertIn("temporary-binding assets say whether they still control route composition", production_delivery)
        self.assertIn("touched route families have an explicit content source status", production_delivery)
        self.assertIn("route-family owner and metadata owner are defined", production_delivery)
        self.assertIn("route-data source of truth is named", production_delivery)
        self.assertIn("route-data source owner", production_delivery)
        self.assertIn("content source status for each touched route family", production_delivery)
        self.assertIn("metadata and route/data integrity result", production_delivery)
        self.assertIn("sitemap/RSS/robots or equivalent feed/output integrity result", production_delivery)
        self.assertIn("generated route-mockup coverage status when applicable", production_delivery)
        self.assertIn("inherited authority versus route-specific authority when generated route owners remain active", production_delivery)
        self.assertIn("active escalation target for unresolved route owners", production_delivery)
        self.assertIn("weakest required route and why it still limits the overall claim", production_delivery)
        self.assertIn("unresolved placeholder-brand drift", production_delivery)
        self.assertIn("unresolved slug collisions, route-data drift, or feed/output mismatch", production_delivery)
        self.assertIn("route evidence status for each touched core route", production_delivery)
        self.assertIn("Readiness Claim Rules", production_delivery)
        self.assertIn("weakest required route evidence status", production_delivery)
        self.assertIn("## Route Evidence", qa_report_template)
        self.assertIn("Route-data integrity status", qa_report_template)
        self.assertIn("Metadata integrity status", qa_report_template)
        self.assertIn("Feed/output integrity status", qa_report_template)
        self.assertIn("Generated route-mockup coverage status", qa_report_template)
        self.assertIn("Inherited authority notes", qa_report_template)
        self.assertIn("Active escalation target", qa_report_template)
        self.assertIn("Weakest route limiting reason", qa_report_template)
        self.assertIn("Data/Metadata Integrity", qa_report_template)
        self.assertIn("Source Owner", qa_report_template)
        self.assertIn("Blocking Failures", qa_report_template)
        self.assertIn("Accepted Gaps", qa_report_template)
        self.assertIn("Overall route evidence status", qa_report_template)
        self.assertIn("Final readiness claim follows weakest required route evidence status", qa_report_template)
        self.assertIn("## Continuation Ownership", qa_report_template)
        self.assertIn("Route owner follow-up", qa_report_template)
        self.assertIn("Route/data drift owner", qa_report_template)
        self.assertIn("Unresolved blocker owner", qa_report_template)
        self.assertIn("Next-session verification target", qa_report_template)
        self.assertIn("Handoff artifact", qa_report_template)
        self.assertIn("Route owner", mock_asset_template)
        self.assertIn("Concept selected from", mock_asset_template)
        self.assertIn("Required route expansion", mock_asset_template)
        self.assertIn("Hardest viewport covered", mock_asset_template)
        self.assertIn("Route-mockup escalation target", mock_asset_template)
        self.assertIn("Route family", mock_asset_template)
        self.assertIn("Inherited from selected concept", mock_asset_template)
        self.assertIn("Route-mockup coverage", mock_asset_template)
        self.assertIn("Escalation target", mock_asset_template)
        self.assertIn("Readiness limiter", mock_asset_template)
        self.assertIn("Upgrade queue", mock_asset_template)
        self.assertIn("Next verification target", mock_asset_template)
        self.assertIn("Blocker owner", mock_asset_template)
        self.assertIn("Active upgrade queue", mock_asset_template)
        self.assertIn("Validate, replace, or retire next", mock_asset_template)
        self.assertIn("Replacement trigger", mock_asset_template)
        self.assertIn("Authority Reason", visual_inventory_template)
        self.assertIn("Route Family", visual_inventory_template)
        self.assertIn("Readiness Limiter", visual_inventory_template)
        self.assertIn("Upgrade Queue", visual_inventory_template)
        self.assertIn("Next Verification Target", visual_inventory_template)
        self.assertIn("Blocker Owner", visual_inventory_template)
        self.assertIn("Replacement Trigger", visual_inventory_template)
        self.assertIn("Generation Entry Conditions", concept_generation)
        self.assertIn("record why the stronger non-generated source paths were not sufficient", concept_generation)
        self.assertIn("required routes and hardest viewports", concept_generation)
        self.assertIn("required route-mockup expansion still to be produced", concept_generation)
        self.assertIn("Only move it to `binding-route`", concept_generation)
        self.assertIn("inherits authority from the selected concept", concept_generation)
        self.assertIn("route-mockup coverage is explicit", concept_generation)
        self.assertIn("route-mockup escalation target is explicit", concept_generation)
        self.assertIn("route ownership, route-mockup coverage, and next verification target", concept_generation)
        self.assertIn("replacement trigger is explicit", concept_generation)
        self.assertIn("do not generate merely because generation is available", concept_generation)
        self.assertIn("`production`", content_readiness)
        self.assertIn("`curated`", content_readiness)
        self.assertIn("`placeholder`", content_readiness)
        self.assertIn("`generated-draft`", content_readiness)
        self.assertIn("`mixed`", content_readiness)
        self.assertIn("route family owner", content_readiness)
        self.assertIn("metadata owner", content_readiness)
        self.assertIn("Framework-Ready Allowances", content_readiness)
        self.assertIn("Visual Delivery Ready Expectations", content_readiness)
        self.assertIn("Metadata And Route/Data Integrity", content_readiness)
        self.assertIn("Readiness Blockers", content_readiness)
        self.assertIn("placeholder-brand drift", content_readiness)
        self.assertIn("route-mockup coverage and escalation target are named when generated assets still shape routes", framework_delivery)
        self.assertIn("Preserve resume-critical route, QA, and blocker state", skill_text)
        self.assertIn("any required route is blocked or not checked", skill_text)
        self.assertIn("handoff continuity", repo_readme)
        self.assertIn("framework-first delivery", repo_readme)
        self.assertIn("memory-aware handoff continuity", repo_readme)

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
            "Current route matrix slice",
            "Temporary-binding assets",
            "Weakest route evidence status",
            "Weakest route limiting reason",
            "Generated route-mockup coverage status",
            "Inherited authority summary",
            "Active escalation target",
            "Production review",
            "Next evidence target",
            "Blocker owner",
            "Handoff artifact",
            "decisions.md",
            "Another session needed",
        ]:
            self.assertIn(expected, template)


if __name__ == "__main__":
    unittest.main()
