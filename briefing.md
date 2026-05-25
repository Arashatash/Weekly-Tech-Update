# Weekly AI Strategy Briefing — Week 22, May 25 – May 31, 2026

> Harnesses eat models: AGI rhetoric peaks while compute, memory and energy quietly become the real moat.

Frontier labs spent the week pitching AGI-imminent narratives (Hassabis's 'foothills of the singularity' at I/O, Sequoia's '2026: This is AGI', Brockman's 70-80% AGI framing) while the real action moved one layer down: agent harnesses (Antigravity, Stitch, Code with Claude) replaced raw models as the product surface, and compute/memory/power emerged as the genuine bottleneck. Capital is bifurcating into two clear plays — vertical 'services-as-software' (Sequoia) and the agent-native infra/dev-tools stack (a16z) — with horizontal wrapper apps quietly being defunded.

---

## Capital & Theses

### Services-as-Software: VC re-rates labor markets
**Source:** Sequoia Capital | **Signal:** high

Sequoia is openly framing AI's next trillion-dollar surface as services replaced by software-priced agents, not seat-based SaaS. The thesis re-rates TAM from IT budgets to labor budgets and tells founders to price on outcomes/headcount-equivalent, not licenses. Capital will follow agent companies that can underwrite SLAs against a human baseline.

[Read more →](https://sequoiacap.com/article/services-the-new-software/)

---

### AGI-as-product-narrative: foothills of the singularity
**Source:** MIT Technology Review | **Signal:** high

Hassabis explicitly tied Google's product stack to AGI/singularity language at I/O 2026, mirrored by Sequoia's '2026: This is AGI' post. Frontier labs are pricing and pitching against an AGI-imminent narrative, which is how they justify $100B+ capex and trillion-dollar IPO chatter. Operators should expect customer procurement cycles to compress as buyers fear being on the wrong side of the curve.

[Read more →](https://www.technologyreview.com/2026/05/22/1137813/google-i-o-showed-how-the-path-for-ai-science-is-shifting/)

---

### Compute & memory as the binding constraint
**Source:** Y Combinator | **Signal:** high

Epoch shows memory is now ~two-thirds of AI chip component cost, while Brockman repeats that compute, not algorithms, is the scarce resource. The investable conclusion: HBM suppliers, custom-silicon design houses, power/cooling, and inference-efficiency tooling are the durable picks-and-shovels — not another wrapper. Anyone selling efficiency (sparsity, KV-cache, fallback routing) gets a procurement audience this year.

[Read more →](https://epoch.ai/data-insights/ai-chip-component-cost-shares)

---

### Agent-native developer tooling consolidates
**Source:** a16z | **Signal:** high

a16z's run of dev-tooling bets (GitButler, Exa, Glif, Tessera) plus Anthropic's Code with Claude event signal a thesis that the IDE/git/search stack gets rebuilt around agents, not humans. Winners will own the agent's working memory and review surface. Incumbents (GitHub, Atlassian) are now defenders, not category leaders.

[Read more →](https://a16z.com/announcement/investing-in-gitbutler/)

---

### AI-search visibility as the new SEO budget
**Source:** TechCrunch | **Signal:** medium

Peec hitting $10M ARR in months tracking brand presence in AI answers validates that marketing spend is migrating from Google SERPs to LLM citations. Expect a fast-forming category (AI-SEO / answer-engine optimization) with 2-3 winners and a clear playbook for any horizontal SaaS to attach. CMO budget is the line item to chase in 2026 H2.

[Read more →](https://techcrunch.com/2026/05/23/peec-one-of-berlins-rising-startups-more-than-doubled-annualized-revenue-in-months-to-10m-sources-say/)

---

## What's Being Built

### Anthropic's Code with Claude: shipping-by-agent becomes default
**Source:** MIT Technology Review | **Signal:** high

Anthropic's London developer event normalized the idea that PRs written end-to-end by Claude are now the median, not the exception. This puts pressure on every dev-tools roadmap to rebuild around agent review, sandboxed execution, and policy controls. Operators not retooling workflow this quarter will fall behind on cycle time within 2 sprints.

[Read more →](https://www.technologyreview.com/2026/05/21/1137735/anthropics-code-with-claude-showed-off-codings-future-whether-you-like-it-or-not/)

---

### Google I/O 2026: Gemini stack collapses into agent harnesses
**Source:** MIT Technology Review | **Signal:** high

I/O bundled Antigravity, Stitch, Gemini 3.5/Omni, and WeatherNext under a single agent-harness narrative — Google is no longer selling models, it's selling orchestrated outcomes. The strategic implication: standalone model APIs commoditize faster, and the moat shifts to harnesses + distribution. Anyone selling 'API access to a frontier model' needs a vertical wedge.

[Read more →](https://www.technologyreview.com/2026/05/22/1137813/google-i-o-showed-how-the-path-for-ai-science-is-shifting/)

---

### DeepSeek Reasonix: cheap, cached coding agent from China
**Source:** Y Combinator | **Signal:** high

A high-caching, low-cost native coding agent on the HN front page reinforces that price/perf parity in coding is no longer a US-only story. This compresses margins for closed-source coding copilots and strengthens the open-source-AI thesis Horowitz is pushing. Enterprises will start dual-sourcing coding agents on cost grounds within 2 quarters.

[Read more →](https://esengine.github.io/DeepSeek-Reasonix/)

---

### Stitch 3.0 by Google
**Source:** Product Hunt | **Signal:** high

Validates AGI-as-product-narrative: foothills of the singularity: Stitch 3.0 ships Google I/O's design-to-code agent as a real product, turning the AGI keynote rhetoric into a concrete workflow that compresses design→prod cycles. It's the clearest operator-level proof that the harness story Hassabis pitched is actually shippable today.

[Read more →](https://www.producthunt.com/products/stitch-by-google)

---

### Google Antigravity CLI
**Source:** Product Hunt | **Signal:** high

Validates Agent-native developer tooling consolidates: Antigravity CLI exposes Google's autonomous-engineering harness (the one that reportedly built an OS for <$1k) directly to developers, mirroring Anthropic's Code-with-Claude push. It confirms that the IDE/CLI surface is being rebuilt around agents — and that the platform wars now run through dev tooling.

[Read more →](https://www.producthunt.com/products/google-antigravity)

---

## Opportunities Now

### Edgee Fallback Models
**Source:** Product Hunt | **Signal:** high | **Horizon:** 0-6 mo

Validates Compute & memory as the binding constraint: Edgee routes inference across providers with automatic fallback, directly monetizing the compute-scarcity reality Brockman keeps describing. Operators can deploy this now to cut inference cost 20-40% and survive provider rate-limit outages — a wedge any infra-savvy team can ship inside a quarter.

[Read more →](https://www.producthunt.com/products/edgee)

---

### Answer-engine optimization agency/tooling play
**Source:** TechCrunch | **Signal:** high | **Horizon:** 0-6 mo

Who: bootstrapped SEO operators and B2B marketing SaaS. What has to be true: brands keep panicking about disappearing from Google AI Overviews and ChatGPT citations. When: 6 months. Peec's $10M ARR ramp shows budget is already moving; the gap is mid-market tooling priced under Peec's enterprise tier.

[Read more →](https://techcrunch.com/2026/05/23/peec-one-of-berlins-rising-startups-more-than-doubled-annualized-revenue-in-months-to-10m-sources-say/)

---

### Agent-trajectory data labeling / RL evals
**Source:** Hugging Face Papers | **Signal:** medium | **Horizon:** 0-6 mo

Who: data-labeling shops and forward-deployed eval teams. What has to be true: long-context agent training (ACC, DelTA) keeps hitting trajectory-data bottlenecks. When: 0-6 months. Every frontier lab is buying trajectory data and verifiable-reward pipelines right now; small specialist firms can land $1-5M ACV contracts before the category gets in-housed.

[Read more →](https://huggingface.co/papers/2605.21850)

---

### Spreadsheet-RL operator wedge
**Source:** Hugging Face Papers | **Signal:** medium | **Horizon:** 0-6 mo

Who: finance/ops vertical SaaS founders. What has to be true: spreadsheet automation via RL'd agents reaches good-enough accuracy on realistic tasks. When: 6 months. The Spreadsheet-RL paper plus the services-as-software thesis means anyone shipping an audited Excel agent for FP&A, RevOps, or insurance underwriting can win paid pilots immediately.

[Read more →](https://huggingface.co/papers/2605.22642)

---

## Opportunities Mid-term

### Outcome-priced services-as-software roll-ups
**Source:** Sequoia Capital | **Signal:** high | **Horizon:** 6-18 mo

Who: PE-backed operators and AI-native founders. What has to be true: agent reliability hits ~95% on bounded workflows (legal intake, claims adjudication, tax prep). When: 6-18 months. The Sequoia thesis points to acquiring sleepy services businesses and re-pricing them on AI margins — early movers in legal, accounting and insurance BPO will set the comp set.

[Read more →](https://sequoiacap.com/article/services-the-new-software/)

---

### Inference-efficiency IP (sparse attention, KV compression)
**Source:** Hugging Face Papers | **Signal:** medium | **Horizon:** 6-18 mo

Who: ex-lab researchers spinning out. What has to be true: full-attention→sparse transfer (and WorldKV-style memory compression) generalizes across model families. When: 12-18 months. With memory at two-thirds of chip BOM, any drop-in technique that cuts KV-cache 3-5x is acquisition bait for hyperscalers and inference clouds.

[Read more →](https://huggingface.co/papers/2605.16928)

---

### AI-native wealth and SMB financial advisory
**Source:** Sequoia Capital | **Signal:** medium | **Horizon:** 6-18 mo

Who: fintech founders with compliance DNA. What has to be true: regulators allow AI co-pilots to deliver bounded fiduciary advice. When: 12-18 months. Sequoia's Nevis bet signals the asset-management vertical is the next services-as-software target after legal/coding; sub-$1M HNW clients are an underserved wedge.

[Read more →](https://sequoiacap.com/article/nevis-bringing-ai-to-wealth-management/)

---

### Personality- and persuasion-aware multimodal agents
**Source:** Hugging Face Papers | **Signal:** medium | **Horizon:** 6-18 mo

Who: consumer and B2B sales/CX startups. What has to be true: MLLMs reliably read user state without crossing manipulative-design lines. When: 12-18 months. The 'Perception or Prejudice' work plus π-Bench proactive-assistant evals show the research is moving fast; sales-coaching and elderly-care agents are the most defensible early markets.

[Read more →](https://huggingface.co/papers/2605.22109)

---

## Opportunities Long-term

### Open-source AI as US industrial policy
**Source:** a16z | **Signal:** medium | **Horizon:** 18+ mo

Who: open-weight model labs, sovereign-AI vendors, on-prem inference startups. What has to be true: a16z's lobbying narrative converts into US policy that subsidizes open weights against DeepSeek/Qwen. When: 18-36 months. If it lands, the value shifts from closed APIs to whoever owns the open-weight distribution and fine-tuning surface — a once-a-decade re-platforming.

[Read more →](https://a16z.com/podcast/ben-horowitz-why-open-source-ai-will-determine-americas-future-2/)

---

### World models for embodied/robotic foundations
**Source:** MIT Technology Review | **Signal:** medium | **Horizon:** 18+ mo

Who: robotics, AV, and simulation startups. What has to be true: PhysX-Omni-style unified simulators and Genie-class world models scale to real physical robots. When: 24-36 months. The companies that own a simulation-to-real pipeline plus proprietary trajectory data become the 'Android of robots' — Nvidia, Google DeepMind and a handful of startups are the live candidates.

[Read more →](https://www.technologyreview.com/2026/05/21/1137756/roundtables-can-ai-learn-to-understand-the-world/)

---

### AI-driven scientific discovery as a productized service
**Source:** Hugging Face Papers | **Signal:** low | **Horizon:** 18+ mo

Who: bio, materials and climate-tech founders. What has to be true: agentic scientists move from 'real but narrow contributions' to defensible IP generation. When: 24-48 months. Isomorphic Labs is the template; expect 5-10 vertical 'AI-first labs' priced like biotechs but with software gross margins to emerge as a new asset class.

[Read more →](https://huggingface.co/papers/2605.22681)

---

### Orbital and gas-powered AI compute
**Source:** TechCrunch | **Signal:** low | **Horizon:** 18+ mo

Who: energy/AI infra hybrids. What has to be true: terrestrial power siting (especially nuclear/gas) and SpaceX-style orbital data-center experiments become economically real. When: 36+ months. Musk's xAI gas pivot plus orbital DC ambitions reveal that compute siting is the next regulatory battleground; investors who can underwrite power+compute together get a structural edge.

[Read more →](https://techcrunch.com/2026/05/23/elon-musk-has-given-up-on-solar-power-on-earth/)

---

## Leader Voices

### Demis Hassabis — Google DeepMind
**Stance:** Bullish

Closing Google I/O 2026, Hassabis said this moment may later be seen as standing at the start of the singularity, calling it a significant moment for humanity and framing AGI as 'the era we're in' rather than a distant horizon.

Google is now explicitly underwriting product strategy to an AGI-imminent narrative; expect every Gemini/Antigravity release to be pitched as a step on that path, which pressures competitors to match the rhetoric or lose mindshare with enterprise buyers.

[Source →](https://www.semafor.com/article/05/20/2026/google-exec-demis-hassabis-predicts-were-at-the-foothills-of-the-singularity)

---

### Greg Brockman — OpenAI
**Stance:** Bullish

In his recent Knowledge Project interview Brockman said it's now hard to know what percent of OpenAI's code is NOT written by AI, that AGI is '70-80% there' by his personal definition, and that compute — not algorithms — is the binding constraint, with 'not going to be enough compute' to meet demand.

Operators should plan workflows around AI-first coding now; investors should overweight compute, memory and inference-routing rather than yet another coding wrapper.

[Source →](https://fs.blog/knowledge-project-podcast/greg-brockman/)

---

### Ben Horowitz — Andreessen Horowitz
**Stance:** Bullish

In a new a16z podcast Horowitz argues that open-source AI will determine America's future, framing open weights as a national-security and economic competitiveness imperative versus Chinese open-source progress.

Expect a16z to lobby aggressively for open-weight-friendly policy and to fund the open-source distribution layer; closed-API-only startups should plan for a more competitive 18-month horizon.

[Source →](https://a16z.com/podcast/ben-horowitz-why-open-source-ai-will-determine-americas-future-2/)

---

### Roelof Botha (and Sequoia partners) — Sequoia Capital
**Stance:** Bullish

Sequoia's AI Ascent 2026 and accompanying essays ('2026: This is AGI', 'Services: The New Software', 'The $10 Trillion AI Revolution') argue AI is moving from selling software to selling labor outcomes, framing a multi-trillion-dollar services TAM as the real prize.

Sequoia is signaling its portfolio construction will favor vertical agent companies priced on outcomes/headcount-equivalent; founders pricing by seats are pitching into a closing thesis window.

[Source →](https://sequoiacap.com/article/services-the-new-software/)

---

### Elon Musk — xAI / SpaceX
**Stance:** Bullish

Musk has effectively abandoned terrestrial solar in his AI plans: xAI is going all-in on natural gas for its compute build-out while SpaceX is pushing orbital data centers as a longer-term compute frontier.

Energy siting — not chips — is becoming the next gating factor for frontier compute. Expect xAI and hyperscaler procurement to drive a step-change in gas-turbine and SMR orders through 2027.

[Source →](https://techcrunch.com/2026/05/23/elon-musk-has-given-up-on-solar-power-on-earth/)

---

### Dario Amodei (via Anthropic Code with Claude) — Anthropic
**Stance:** Bullish

At Code with Claude in London, Anthropic positioned PRs written end-to-end by Claude as the new median for developers — staff repeatedly asked attendees who had shipped fully AI-written code in the past week, treating it as the baseline expectation.

Anthropic is locking in the 'agent-as-developer' positioning; dev-tool vendors that don't natively support multi-agent review and sandboxed execution within two quarters will lose the next procurement cycle.

[Source →](https://www.technologyreview.com/2026/05/21/1137735/anthropics-code-with-claude-showed-off-codings-future-whether-you-like-it-or-not/)

---

### Chi Xu — XREAL
**Stance:** Bullish

XREAL's CEO told TechCrunch the smart-glasses industry has reached a turning point, framing Google's partnership and AI-assistant integration as the inflection that finally makes the form factor consumer-viable.

Ambient/wearable AI is the next consumer surface after the phone; companies betting on chat UIs alone risk missing a hardware-driven distribution shift in 2027-2028.

[Source →](https://techcrunch.com/2026/05/24/xreal-googles-smartglasses-partner-thinks-it-has-finally-mastered-this-notoriously-tricky-industry/)

---

## Commentary Synthesis: Investors vs Operators

AI in late May 2026 is in a strange equilibrium: capability claims (Hassabis on the 'foothills of the singularity', Brockman on 80% AI-written code) are running well ahead of measured enterprise productivity (NBER finds most AI-using firms still report no productivity gains). What is real and well-evidenced this week: (1) agent harnesses, not raw models, are now the product surface — Google's Antigravity/Stitch and Anthropic's Code-with-Claude both proved it; (2) memory and power, not algorithms, are the binding constraints — Epoch's data showing memory at two-thirds of chip BOM is the most underdiscussed chart of the month; (3) capital is rotating from horizontal LLM apps to either deep-vertical 'services-as-software' (Sequoia) or open-source/dev-tools infra (a16z). Expect the next 6 months to be defined by a brutal margin squeeze on thin GPT-wrappers, the first credible IPO comps for agentic services companies, and an intensifying compute-siting fight (gas, nuclear, possibly orbital). The honest read: this is a real platform shift, but the AGI rhetoric is partially a financing narrative to justify $100B+ capex cycles.

| Topic | Investor View | Operator View | Practical Implication |
|---|---|---|---|
| **How close is AGI?** | Sequoia's '2026: This is AGI' and a16z's open-source AI push treat AGI-adjacent capability as the working assumption for portfolio construction. | Hassabis says 'foothills of the singularity' but separately maintains ~50% probability by 2030; Brockman says AGI is '70-80% there' by his definition but stresses jaggedness. | *Plan capital deployment as if powerful agents arrive in 18-36 months, but underwrite revenue on today's jagged capability — don't pre-spend on speculative AGI margins.* |
| **Where is the moat?** | VCs are funding agent harnesses, vertical services-as-software, and infra (memory, routing, evals). Wrapper apps are getting passed on. | Frontier labs say the moat is compute + distribution; DeepSeek Reasonix and open weights are eroding pure-model moats fast. | *Founders must own either proprietary workflow data, a regulated vertical, or an efficiency primitive. Pure API resellers are uninvestable by Q4 2026.* |
| **What's the binding constraint?** | Sequoia/a16z increasingly write about distribution and GTM as the bottleneck, given model commoditization. | Brockman: 'there's not going to be enough compute' — memory, power and GPUs gate everything. | *Both are right at different layers. Picks-and-shovels investors should overweight memory/power/inference-routing; app investors should overweight distribution and embedded workflow.* |
| **Coding automation** | a16z's GitButler/Exa/Tessera bets assume the IDE+git+search stack is fully re-platformed around agents within 24 months. | Anthropic and OpenAI internally report 70-80% of code written by AI; external NBER data shows most enterprises see no productivity lift yet. | *There's a 12-18 month gap between lab-internal productivity and enterprise reality. The arbitrage is selling the workflow retooling (training, change management, governance), not just the model.* |

---

## Follow the Money

| Trend Type | Observation | Implication |
|---|---|---|
| **Infra Spend** | Epoch shows memory now ~two-thirds of AI chip component cost; Brockman frames compute (not algorithms) as the binding constraint and says OpenAI is treating compute as a revenue center. | HBM suppliers (SK Hynix, Micron, Samsung) and inference-efficiency startups are structurally favored. Expect a wave of secondary-market memory shortages and a new round of HBM-focused fundraises by H2. |
| **Capital Flow** | a16z announced ~10 AI-adjacent investments this week (Exa, Stitch, Ethos, Tessera, Glif, Petual, Ulysses, Hilbert, GitButler, Stipple Bio, Treeline) skewed toward dev-tools, search/retrieval and bio. | a16z is concentrating into the agent-tooling and vertical-AI stack; founders in horizontal chat/wrapper plays should not expect a16z term sheets in 2026. |
| **Enterprise Spend** | Peec reportedly doubled to $10M ARR in months selling AI-search-visibility tracking; Ferrari/IBM deployed AI for F1 fan engagement. | CMO budgets are the fastest-moving line item in AI right now. Marketing-tech founders have a 12-month window before incumbents (Adobe, HubSpot, Salesforce) bundle answer-engine optimization for free. |
| **Infra Spend** | OpenAI raised $122B in 2026 and is targeting a potential $1T IPO; Musk's xAI is pivoting to natural gas and SpaceX is exploring orbital data centers. | Power siting is the next gating factor after chips. Energy-AI hybrids and behind-the-meter gas/nuclear projects will see record VC and infra-fund interest in 2026 H2. |
| **Acquisition Or Bet** | Sequoia's 'Services: The New Software' and Nevis (AI wealth management) bet, plus Ineffable Intelligence ('superlearner'), signal a concentrated push into agentic services replacing labor cost centers. | Expect Sequoia-led roll-ups in legal, accounting, insurance BPO and wealth management within 12 months — set comp tables now. |
| **Overheated Signal** | Hassabis closing I/O with 'foothills of the singularity', Sequoia titling a post '2026: This is AGI', and OpenAI floating $1T IPO chatter — all in the same fortnight. | Narrative density is at a local maximum. Late-stage AI valuations are pricing AGI-imminent; any earnings miss or capability plateau in H2 could trigger a sharp multiple compression in pure-AI public comps. |
| **Capital Flow** | Deep Fission filing for a $157M IPO and Boston Metal raising $75M for critical metals reflect adjacent capex flooding into anything labeled 'AI power' or 'AI supply chain'. | Watch for label-washing: non-AI energy/materials companies will increasingly market themselves as AI infra. Diligence the actual offtake agreements, not the pitch deck. |

---

## Top Signals

### 1. Agent harnesses, not models, are now the product — retool dev and procurement workflows this quarter
**Urgency:** Act now

Google's Antigravity/Stitch and Anthropic's Code with Claude make it clear that the buying unit has shifted from API access to orchestrated agent workflows. Teams still selling or buying raw model access are competing on the wrong axis.

### 2. Memory is now ~2/3 of AI chip BOM — re-price your infra thesis
**Urgency:** Act now

Epoch's data plus Brockman's 'not enough compute' framing means HBM and inference-efficiency are the structural winners. Anyone allocating to AI infra without an explicit memory/power view is mispriced.

### 3. Services-as-software roll-ups are the next investable category
**Urgency:** Act now

Sequoia's essay stack and Nevis bet telegraph a coming wave of agent-powered acquisitions in legal, accounting, insurance and wealth management. Operators should map acquirable targets now; investors should set comp tables before the first marquee deal prints.

### 4. AGI narrative density is at a local maximum — watch for multiple compression
**Urgency:** Watch closely

When Hassabis, Sequoia and OpenAI all invoke AGI/singularity in the same fortnight while NBER finds 80% of AI-using firms see no productivity gain, the gap between rhetoric and revenue is widening. Any H2 capability plateau will hit late-stage AI valuations hard.

### 5. Energy siting (gas, nuclear, orbital) is the next regulatory battleground
**Urgency:** Stay informed

Musk's xAI gas pivot and SpaceX orbital DC plans, plus Deep Fission's IPO attempt, show compute power is moving from a procurement problem to a permitting and policy problem. Infra investors need an energy/permitting thesis, not just a GPU thesis.
