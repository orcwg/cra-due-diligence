# Appendix A: Running a project's test vectors in an integrator's build

This appendix works through the example that chapter 5 refers to.
It is one illustration of a vector set, a manifest and a runner, not a recommendation of a particular tool.

## The setting

An integrator's product embeds a library that verifies signed evidence records.
The library's own project ships no test data.
The integrator uses a published vector set for that record format, agent-evidence-vectors release 0.25.0 (`agent-evidence-vectors==0.25.0` on PyPI).
The release carries 288 vectors, a manifest that lists every vector with its expected result and pins the whole set by one digest, and a runner that feeds each vector to the component and compares its answer with the expected one.
Each vector is a record paired with the result the library must return for it.

The component under test is called through a small command that reads a record and prints its verdict as JSON.
In this example the verifier published with the vectors stands in for the integrator's library, so anyone can repeat the run.

## The commands

The first three commands build the stand-in component from the release commit.
The last one is the runner, which an integrator would put in the product's build.

```sh
git init -q vectors-src && cd vectors-src
git fetch -q --depth 1 https://github.com/probityai/agent-evidence-vectors.git e7508ced37dacc89decacd857e97930860ee08cd
git checkout -q FETCH_HEAD && go build -o ../component ./cmd/aee-verify && cd ..
uvx agent-evidence-vectors==0.25.0 --verifier './component -validity-only -json'
```

In an integrator's build, `./component` is the integrator's own build of the library behind the same small command.

## Reading the output

The runner prints one row per vector and then a totals line.

```text
vector                                     status gate0      gate1      recompute  tier       self-check
vcf20eae7df4f1f1b                          PASS   PASS       PASS       PASS       PASS       -
...
totals: 288 vectors, 288 pass, 0 fail; report written to conformance-report.json
verifier: ./component -validity-only -json ran on 288 of 288 vectors
```

The status column is the result for each vector, and the totals line counts it.
The runner exits with status 0 when every vector passes and 1 otherwise, so a build step fails on any changed result.
The columns after status name the stage of the check at which the component accepted or rejected the record.
They help the project find a fault and are not part of the integrator's result.
A stage column can read FAIL on a vector whose status is PASS, when the component rejected the record at an earlier stage than the vector also lists.

## What a failure looks like

To show that the run detects a missing check, build a copy of the component with one check removed: the check that a list of commitments is non-empty, sorted and free of duplicates.
Run against that copy, the same command exits with status 1, reports `totals: 288 vectors, 287 pass, 1 fail`, and the row for vector `v0ac6d948f2af5b6f` reads FAIL in the status column.
That vector is a record the library must reject with the code `payload-commitment-malformed`, and the copy accepts it.

## What the integrator records

The integrator keeps the run output and the report file, and records their digests as one checked property in the chapter 3 record, together with the vector release and the component revision the manifest pins.
The run shows that the rules these vectors cover are enforced in the build the integrator ships.
It says nothing about the rest of the library.
