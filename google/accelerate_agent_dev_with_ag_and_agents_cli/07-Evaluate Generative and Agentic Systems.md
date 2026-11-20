<link rel="stylesheet" href="./tabs.css">

# Evaluate Generative and Agentic Systems

Deploying reliable generative and agentic systems requires moving beyond traditional software testing and subjective assessments. Because these probabilistic systems introduce unique failure modes, technical teams need structured frameworks to measure quality, enforce guardrails, and tie model behavior directly to business outcomes. This lesson gives engineers and architects practical tools to design, execute, and scale rigorous evaluation pipelines. You will master the full evaluation hierarchy, from fast deterministic checks to calibrated Large Language Model (LLM) autoraters and human-in-the-loop workflows. Learn how to simulate high-fidelity test datasets, trace multi-turn agent trajectories, and establish reliable consistency metrics across runs. By the end of this lesson, you will be prepared to translate organizational Key Performance Indicators (KPIs) into actionable technical benchmarks, calibrate objective rubrics, and maintain a continuous quality flywheel from initial offline experiments through live production monitoring. 

## Foundations of generative AI evaluation

Custom evaluation strategies are essential when you're working with generative and agentic systems. Because these models are probabilistic, standard tests and generic public benchmarks won't give you the full picture. If you want to build dependable systems that deliver real value for your organization, you need an evaluation-driven strategy tailored to your specific use case. 

In this module, you'll explore the main hurdles of evaluating generative artificial intelligence (AI) and agentic systems, including unpredictability and the "oracle problem," where verifying the right answer isn't always straightforward. You'll see how tailored evaluations protect against business risk and keep you from relying on static benchmarks. Finally, you'll walk through a six-stage lifecycle that guides your system all the way from initial goals to live telemetry monitoring. 

### Making the case for custom evaluation

Generative artificial intelligence (AI) models are probabilistic, so traditional software testing just isn't enough. Standard tests often miss nuanced issues like hallucinations, sycophancy, and instruction drift. With a custom evaluation plan, you can catch these behaviors early and make sure your system delivers on your organization's goals. 

To get there, you need tailored evaluations rather than static public benchmarks—helping you avoid the unpredictable performance swings known as the "ragged edge." 

#### The generative AI uncertainty challenge

In traditional software development, you write code to produce predictable, deterministic outputs. A specific input always yields the exact same output. Generative AI breaks this model. Because generative AI models are probabilistic, they are inherently non-deterministic. The same prompt can produce different responses each time you run it.

This uncertainty introduces three core challenges when you evaluate generative AI systems:

1. **Stochasticity or non-determinism:** You can't rely on simple string matching to verify responses. Instead of expecting single static values, you need flexible definitions of correctness that account for natural variations in phrasing.
2. **Capability variability:** Model performance is inconsistent. A model might handle highly complex logic perfectly, yet fail on a seemingly simple task (sometimes called _"jagged edge"_ or _"ragged edge"_ or _"jagged frontier"_.)
3. **The oracle problem:** For generative tasks like summarizing a document or writing an email, there is no single "correct" answer. Because there isn't one ground-truth output, writing rigid programmatic checks becomes resource-intensive and often impossible.

These challenges appear as distinct failure modes in applications using generative AI models:

<div class="md-tabs">
  <input type="radio" name="platform-capabilities" id="tab-plat-capab-1" checked>
  <label for="tab-plat-capab-1">Hallucinations</label>
  <input type="radio" name="platform-capabilities" id="tab-plat-capab-2">
  <label for="tab-plat-capab-2">Sycophancy</label>
  <input type="radio" name="platform-capabilities" id="tab-plat-capab-3">
  <label for="tab-plat-capab-3">Instruction Drift</label>
  <div class="tab-panel">  
    <p>The model generates factually incorrect but highly plausible assertions.</p>
  </div>
  <div class="tab-panel">
    <p>The model agrees with your incorrect premises or biases to be "helpful," prioritizing compliance over correctness.</p>
  </div>
  <div class="tab-panel">
    <p>The model fails to follow constraints over long conversations, gradually deviating from your original instructions.</p>
  </div>
</div>

**Evaluation is how you ultimately mitigate these issues.**

Developers engage in prompt engineering, model changes, rearchitecture, and other technical fixes to mitigate these issues.

Without quantitative evaluation, you're essentially flying blind. You have no systematic way to measure whether your fixes, prompt tweaks, or guardrails are actually improving the system or quietly breaking something else.

#### Evaluation as risk management 

Organizations adopt generative AI to hit specific targets. 


However, launching probabilistic models without solid evaluation invites major business risks. If a generative system or agent underperforms, your team risks missing key performance indicators (KPIs). That shortfall quickly turns a promising AI initiative into a costly, failed investment.

Beyond missed KPIs, unmeasured systems can cause:
* **Reputation Damage:** Embarassing model outputs can damage customer trust.
* **Legal Liability:** Outputs can accidentally violate compliance standards or laws.

To build support for the time and cost of evaluation, frame it around mitigating risks. For example, if your team is deploying a customer support chatbot, a key KPI might be customer satisfaction.

If the AI frustrates users, satisfaction drops. Therefore, you must evaluate the chatbot to ensure it maintains or increases customer satisfaction levels.

Evaluation is the process of de-risking. You should anchor your evaluation investments directly to the severity of the risks involved.

* **High-risk systems:** These include financial or medical advice tools, that require evaluation that covers function, safety, and compliance. 
* **Low-risk systems:** These include internal brainstorming tools, which require far less evaluation.

#### The public benchmark trap 

When a new model launches, it is usually accompanied by a wave of public benchmarks. These scores show relative progress in model capabilities. However, you cannot substitute public model benchmarks for custom system evaluations.

Public benchmarks are often not applicable to systems you build for several reasons:

* **Data contamination:** The benchmarks are frequently leaked into the models' training data, inflating their performance scores. One experiment changed only the numbers in a math benchmark. Even though the core task remained identical, the models' performance scores dropped significantly.
* **Toy workloads:** Many benchmarks test academic puzzles or multiple-choice questions that fail to represent real-world tasks. The datasets required for realistic testing are often proprietary and unavailable. Benchmarks purporting to measure real-world tasks often fall short when scrutinized against real-world expectations.
* **Ambiguous metrics:** It is often unclear what a public benchmark is measuring, making the score difficult to translate into organizational value.

#### Model benchmarks are primarily marketing tools.

Evaluate the model on your specific needs. _A model that scores 99% on a math benchmark will not automatically translate to a high-performing customer support agent for your specific company_. You must evaluate the model on your specific needs.

**The ragged edge of model capabilities** 

As generative models improve, their capabilities do not scale uniformly. This behavior is called the _"ragged edge"_. Getting better at one task does not guarantee a model will get better at other closely related tasks.

The first generation of useful coding agents is a great example of this phenomenon. Generative AI models got good at producing code that passed a test case far more quickly than they got good at producing code that was highly readable or easy to maintain.

So while "code function" represents one capability generative AI models have come to excel at, "code quality" represents a different but closely related capability that has lagged behind.