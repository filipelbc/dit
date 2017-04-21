# Refactor Plan

## Issues of the Current Implementation

1. The code is lacking orthogonality. Some examples are:
    * Modules are dependent on each other.
    * Code for parsing the stdin is tightly coupled with system logic code.
    * The use of global variables should be avoided.

2. The code is lacking reversibility. Early decisions should be treated as
   configuration options. How hard it would be
    * to use sqlite instead of text files?
    * to have multiple group levels instead of two?
    * to add support to a second language?

3. No contracts.
    * Every class should be designed with a clear invariant.
    * Every routine should have its pre- and post-conditions.

4. No unit tests.
    * Test against contract.
    * Every routine should be decoupled and testable.
    * Tests (and the contracts) should be written before the implementation.

## Pending Decisions/Research

* Keep Python or change to another programming language?
* Database or plain text files?
* How completion should be implemented?
* Tags instead of groups?
* Multi-language support?
* Interactive mode?

## Documentation

* Textual use cases (with hierarchy, cross-links) before the refactor.
* Contracts and unit tests during the refactor.

## Schedule

One day ~ 2h. One week ~ 10h.

1. Write textual use cases ~ 1 week.
2. Quick code review, with suggestions to fix the aforementioned issues ~ 3 days.
3. Define the major classes (some of them will be defined during the refactor) ~ 2 days.
4. Refactor stdin parser ~ 2 days.
5. Refactor index and previous ~ 3 days.
6. Refactor task management ~ 1 week.
7. Refactor data visualization ~ 1 week
7. Refactor the main class and everything else ~ 1 week.

Total work-time: 6 weeks.
