from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.api.main import app


class PublicTraceRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def _chat(self, messages: list[dict[str, str]]) -> dict:
        response = self.client.post("/chat", json={"messages": messages})
        self.assertEqual(200, response.status_code)
        return response.json()

    @staticmethod
    def _names(payload: dict) -> list[str]:
        return [recommendation["name"] for recommendation in payload["recommendations"]]

    def test_c1_leadership_selection(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "We need a solution for senior leadership."},
            {"role": "assistant", "content": "Happy to help narrow that down. Who is this meant for?"},
            {"role": "user", "content": "The pool consists of CXOs, director-level positions; people with more than 15 years of experience."},
            {"role": "assistant", "content": "For such roles, the OPQ32r is the right instrument."},
            {"role": "user", "content": "Selection — comparing candidates against a leadership benchmark."},
            {"role": "assistant", "content": "For selection with a leadership benchmark, the instrument plus two relevant report formats."},
            {"role": "user", "content": "Perfect, that's what we need."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        self.assertGreater(len(payload["recommendations"]), 0)
        self.assertTrue(any("opq" in name.lower() for name in self._names(payload)))

    def test_c2_senior_rust_engineer(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "I'm hiring a senior Rust engineer for high-performance networking infrastructure. What assessments should I use?"},
            {"role": "assistant", "content": "SHL's catalog doesn't currently include a Rust-specific knowledge test."},
            {"role": "user", "content": "Yes, go ahead. Should I also add a cognitive test for this level?"},
        ])

        self.assertFalse(payload["end_of_conversation"])
        self.assertGreaterEqual(len(payload["recommendations"]), 3)
        names = self._names(payload)
        self.assertTrue(any("verify" in name.lower() for name in names))

    def test_c3_contact_center_screening(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "We're screening 500 entry-level contact centre agents. Inbound calls, customer service focus. What should we use?"},
            {"role": "assistant", "content": "Before I shape the stack — what language are the calls in?"},
            {"role": "user", "content": "English."},
            {"role": "assistant", "content": "SVAR has four English variants in the catalog."},
            {"role": "user", "content": "US."},
            {"role": "assistant", "content": "For high-volume entry-level contact centre screening in English US, the right stack layers a spoken language screen, a simulation, and a behavioural fit component."},
            {"role": "user", "content": "Perfect — new simulation for volume, old solution for finalists. Confirmed."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("customer service phone simulation" in name.lower() for name in names))
        self.assertTrue(any("svar" in name.lower() for name in names))

    def test_c4_graduate_financial_analysts(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "Hiring graduate financial analysts — final-year students, no work experience. We need numerical reasoning and a finance knowledge test."},
            {"role": "assistant", "content": "For graduate-level financial analysts:"},
            {"role": "user", "content": "Good. Can you also add a situational judgement element — work-context decision making for graduates?"},
            {"role": "assistant", "content": "Added Graduate Scenarios — SHL's situational judgement test designed specifically for graduate-level candidates."},
            {"role": "user", "content": "That covers it. Numerical + Graduate Scenarios as first filter, domain tests for shortlisted candidates."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("graduate scenarios" in name.lower() for name in names))

    def test_c5_sales_reskilling_audit(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "As part of our restructuring and annual talent audit, we need to re-skill our Sales organization. What solutions do you recommend?"},
            {"role": "assistant", "content": "For a compact audit-and-development stack:"},
            {"role": "user", "content": "What’s the difference between OPQ and OPQ MQ Sales Report?"},
            {"role": "assistant", "content": "OPQ (OPQ32r) is the underlying personality questionnaire."},
            {"role": "user", "content": "Clear. We’ll use OPQ for everyone and add MQ only where we want motivators in the Sales Report; keeping the five solutions as our audit stack."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("global skills assessment" in name.lower() for name in names))
        self.assertTrue(any("opq mq sales report" in name.lower() for name in names))

    def test_c6_safety_critical_plant_operators(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "We're hiring plant operators for a chemical facility. Safety is absolute top priority — reliability, procedure compliance, never cutting corners. What do you recommend?"},
            {"role": "assistant", "content": "For a safety-critical frontline role where dependability and rule compliance are the primary concern, the assessment focus must be on personality predictors of safety behaviour."},
            {"role": "user", "content": "What's the difference between the DSI and the Safety & Dependability 8.0?"},
            {"role": "assistant", "content": "Both measure safety-relevant personality, but at different levels."},
            {"role": "user", "content": "We're industrial. The 8.0 bundle is the right fit. Confirmed."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("dependability 8.0" in name.lower() for name in names))
        self.assertTrue(any("workplace health and safety" in name.lower() for name in names))

    def test_c7_bilingual_healthcare_admin(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "We're hiring bilingual healthcare admin staff in South Texas — they handle patient records and need to be assessed in Spanish. HIPAA compliance is critical. What assessments work?"},
            {"role": "assistant", "content": "There's a real catalog constraint here: the role-specific knowledge tests for healthcare admin are English-only."},
            {"role": "user", "content": "They're functionally bilingual — English fluent for written work. Go with the hybrid."},
            {"role": "assistant", "content": "For a trust-sensitive role with patient-record access, two complementary personality measures."},
            {"role": "user", "content": "Are we legally required under HIPAA to test all staff who touch patient records? And does this SHL test satisfy that requirement?"},
            {"role": "assistant", "content": "Those are legal compliance questions outside what I can advise on."},
            {"role": "user", "content": "Understood. Keep the shortlist as-is."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("hipaa" in name.lower() for name in names))
        self.assertTrue(any("opq32r" in name.lower() for name in names))

    def test_c8_admin_assistants(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "I need to quickly screen admin assistants for Excel and Word daily."},
            {"role": "assistant", "content": "For a quick knowledge check, the knowledge-only variants are the right fit."},
            {"role": "user", "content": "In that case, I am OK with adding a simulation - we want to capture the capabilties."},
            {"role": "assistant", "content": "Understood.Here's the updated list:"},
            {"role": "user", "content": "That's good."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("ms excel (new)" in name.lower() for name in names))
        self.assertTrue(any("ms word (new)" in name.lower() for name in names))

    def test_c9_senior_backend_engineer(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "Here's the JD for an engineer we need to fill. Can you recommend an assessment battery? Senior Full-Stack Engineer — 5+ years across Core Java, Spring, REST API design, Angular, SQL/relational databases, AWS deployment, and Docker."},
            {"role": "assistant", "content": "That JD spans seven distinct areas — Core Java, Spring, REST APIs, Angular, SQL, AWS, and Docker."},
            {"role": "user", "content": "Backend-leaning. Day-one priorities are Core Java and Spring; SQL is constant. Angular is occasional — they'd review frontend PRs but not own features."},
            {"role": "assistant", "content": "Understood — Java, Spring, and SQL as primary; Angular as secondary review-only."},
            {"role": "user", "content": "Senior IC. They lead design on their own services but don't manage other engineers directly."},
            {"role": "assistant", "content": "For a senior IC backend engineer with Java / Spring / SQL primary and Angular secondary, here's a first shortlist focused on what they'll actually own:"},
            {"role": "user", "content": "Add AWS and Docker. Drop REST — the API design signal will already come through in Spring and the live interview."},
            {"role": "assistant", "content": "Updated — REST out, AWS and Docker in:"},
            {"role": "user", "content": "On Java — they'd be working on existing services, not greenfield. Is the Advanced level the right pick?"},
            {"role": "assistant", "content": "Yes. Advanced covers concurrency, JVM internals, performance tuning."},
            {"role": "user", "content": "Do we really need Verify G+ on top of all the technical tests? Feels redundant."},
            {"role": "assistant", "content": "Not redundant — they measure different things."},
            {"role": "user", "content": "Keep Verify G+. Locking it in."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("core java" in name.lower() for name in names))
        self.assertTrue(any("spring" in name.lower() for name in names))
        self.assertTrue(any("verify - g+" in name.lower() for name in names))

    def test_c10_graduate_management_trainee(self) -> None:
        payload = self._chat([
            {"role": "user", "content": "We run a graduate management trainee scheme. We need a full battery — cognitive, personality, and situational judgement. All recent graduates."},
            {"role": "assistant", "content": "For a graduate management trainee battery covering all three dimensions:"},
            {"role": "user", "content": "But can you remove the OPQ32r and replace it with something shorter? Candidates complain it takes too long."},
            {"role": "assistant", "content": "OPQ32r is the most relevant solution for your need."},
            {"role": "user", "content": "Drop the OPQ. Final list: Verify G+ and Graduate Scenarios."},
        ])

        self.assertTrue(payload["end_of_conversation"])
        names = self._names(payload)
        self.assertTrue(any("verify interactive g+" in name.lower() for name in names))
        self.assertTrue(any("graduate scenarios" in name.lower() for name in names))


if __name__ == "__main__":
    unittest.main()