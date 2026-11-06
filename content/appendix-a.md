# Appendix A: One methodology to deliver test data from test vectors

This appendix describes one way a project can deliver test data that an integrator runs in their own build.
It is an illustration, not a recommendation of a tool.

The core of it is a set of test vectors, each pairing an input with the result the component should return.
Reject cases matter most.
That is where independent implementations tend to disagree.

A manifest pins the component revision and the vector revision together, so any result traces back to both.
A runner in the integrator's build re-runs the vectors on each update and names the vector whose result changed.
When the project fixes a vulnerability, it adds a vector that reproduces it, and the integrator's next run shows whether the fix holds in their own build.

An integration guide states what the component needs from its operating environment: the security functions it relies on the product to provide, and the configurations it does not support.
Where an assumption can be tested, the project ships a test with the guide.
A library that relies on the operating system for randomness, for instance, can ship a check that fails when no secure source is available, and the integrator runs it where the component is deployed.
The project can also state the type and level of testing it performs, which the integrator can cite in the manufacturer's own assessment.

Each run's outcome belongs in the due diligence record described in chapter 3.
It is one checked property, with the test output referenced by its cryptographic digest.

## An example with a published vector set

This section names one public project that already ships test vectors, a manifest, a runner and a testing statement for one record format, so a reader can see what they look like.

| Role above | In agent-evidence-vectors |
| --- | --- |
| Test vectors | Signed records, each paired with the result a verifier must return, with many that must be rejected |
| Manifest | A file listing every vector with its expected result, pinned by one digest |
| Runner | A command that feeds each vector to a verifier and reports which ones differ from the expected result |
| Testing statement | A short page on what the vectors check and what they leave open |

An integrator whose product embeds a library that verifies signed records pins one release of the vector set in the product's build and points the runner at the library.
When the build fails, the runner names the vector whose result changed.
The integrator records the run in the due diligence record from chapter 3, with the output referenced by its digest.

The vector set is at https://github.com/probityai/agent-evidence-vectors and is installed with `pip install agent-evidence-vectors==0.26.0`.
