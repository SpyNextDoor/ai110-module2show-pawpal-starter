# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

--> My initial UML design has three classes. The pet class is the parent class which is inherited by Tracking class and DailyPlan class. Since the owner wants to medicate the pet i am think of adding an enum class to identify what health condition the pet is in

- What classes did you include, and what responsibilities did you assign to each?

--> Enum class

class heath:

	sick =  1

	heathy = 2

--> Owner class:

1. attributes: owner_name(str)
2. methods: add_owner(), get_owner()

--> Pet class:

1. attributes: pet_name (str), health_condition (str)
2. methods: add_pet, get_pet

--> Tracking class

1. attributes: _
2. methods: schedule_walk, feed_pet, groom_pet, treat_pet

--> DailyPlan class:

1. attributes: _
2. methods:

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

--> after consulting with claude, I realized that there were so many functionalities my initial design didn't have. We did a heavy lifting in the task and daily plan classes since I had not thought about the constraints like time and priority. 

**This is the new design:**

Class Name: Owner

1. Attributes:

- ownerName: String
- availableMinutes: Integer
- preferences: Dictionary

2. Methods:

- register()
- setAvailableMinutes(minutes: int)
- addPreference(key: String, value: String)

Class Name: Pet

1. Attributes:

- petId: String
- name: String
- species: String
- healthCondition: HealthCondition

2. Methods:

- addTask(task: Task)
- removeTask(taskId: String)
- getTasks(): List<Task></task>

Class Name: Task

1. Attributes:

- taskId: String
- name: String
- taskType: TaskType
- durationMinutes: Integer
- priority: Priority
- preferredTime: String
- recurring: Boolean

2. Methods:

- markDone()
- updatePriority(priority: Priority)

Class Name: DailyPlan

1. Attributes:

- planId: String
- planDate: Date
- scheduledTasks: List

**Changes in the design:** 

After asking claude to look through the skeleton for implementation we might have missed this is what we fixed:

* `DailyPlan.__init__` now takes a `plan_id`, matching the diagram's attribute that the code had dropped.
* `Owner` gained `pets: list[Pet]` plus `add_pet()` / `get_pets()` stubs — closes the missing owner↔pet relationship.
* `Task` gained a `pet: Pet | None` back-reference, so a task can report which pet it belongs to without the pet being passed around separately.
* `DailyPlan` now stores `pet` and `owner` as fields (set by `generate()`), instead of only ever seeing them as transient method parameters — `explain()` and `get_total_minutes()` can now know whose plan they're reporting on.
* `DailyPlan.reasoning` changed from a flat `list[str]` to `dict[str, str]` keyed by `task_id`, so each reason is traceable to the task it belongs to instead of being order-dependent.
* `DailyPlan.generate()` dropped the separate `tasks` parameter — it's now expected to pull tasks from `pet.get_tasks()`, removing the two-sources-of-truth risk.
* Added `from __future__ import annotations` to support the forward references (`Owner.pets: list[Pet]`, `Task.pet: Pet`) without reordering classes.

  **FINAL DESIGN:**



Class Name: Owner

1. Attributes:

- ownerName: String
- availableMinutes: Integer
- preferences: Dictionary
- pets: List of Pet objects

2. Methods:

- register()
- setAvailableMinutes(minutes: int)
- addPreference(key: String, value: String)
- addPet(pet: Pet)
- getPets(): List<Pet></pet>

Class Name: Pet

1. Attributes:

- petId: String
- name: String
- species: String
- healthCondition: HealthCondition

2. Methods:

- addTask(task: Task)
- removeTask(taskId: String)
- getTasks(): List<Task></task>

Class Name: Task

1. Attributes:

- taskId: String
- name: String
- taskType: TaskType
- durationMinutes: Integer
- priority: Priority
- preferredTime: String
- recurring: Boolean
- pet: Pet

2. Methods:

- markDone()
- updatePriority(priority: Priority)

Class Name: DailyPlan

1. Attributes:

- planId: String
- planDate: Date
- pet: Pet
- owner: Owner
- scheduledTasks: List of Task objects
- skippedTasks: List of Task objects
- reasoning: Dictionary with String keys and String values

2. Methods:

- generate(pet: Pet, owner: Owner)
- sortByPriority(tasks: List<Task></task>): List<Task></task>
- fitsInTime(task: Task, remainingMinutes: int): Boolean
- addTask(task: Task, reason: String)
- skipTask(task: Task, reason: String)
- getTotalMinutes(): Integer
- explain(): String

Class Name: HealthCondition (Enumeration)

1. Attributes:

- HEALTHY
- SICK
- RECOVERING
- SENIOR

2. Methods:

- None

Class Name: TaskType (Enumeration)

1. Attributes:

- WALK
- FEEDING
- MEDICATION
- ENRICHMENT
- GROOMING
- OTHER

2. Methods:

- None

Class Name: Priority (Enumeration)

1. Attributes:

- LOW
- MEDIUM
- HIGH

2. Methods:

- None

Class Relationships

- Owner → Pet: One owner owns one or more pets.
- Pet → Task: One pet can have multiple tasks.
- DailyPlan → Owner: Each daily plan is associated with exactly one owner.
- DailyPlan → Pet: Each daily plan is created for exactly one pet.
- DailyPlan → Task: A daily plan contains zero or more tasks through composition.
- Pet → HealthCondition: A pet has a health condition.
- Task → TaskType: Each task has a task type.
- Task → Priority: Each task has a priority.

*DailyPlan is equivalent to **Scheduler** class that was suggested.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

--> I used ai to brainstorm a better design for the app and to generate a scafolding skeleton for the methods I needed. 

- What kinds of prompts or questions were most helpful?

--> I found it helpful to ask the ai agent questions that start with "Role: software developer" this way ai tends to not give you all the solutions at once and it tries to optmize the results it gives you.

--> AI is really good at explaing logics and how the whole design ties together. As an early developer I still struggle to see the big picture and ai helps with that. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

--> When I asked AI to generate the UML/skeleton code I realized that some relations were not tied into the design. For instance, the owner had no way of adding pets, tasks weren't directly linked to the pet they refer to. 

- How did you evaluate or verify what the AI suggested?

--> After realizing this, I asked claude questions about these relations like " how would an owner add pets, can an owner have multiple pets, how will i know which task belong to which pet" this helped ai realize these were missing and went back to implement them and revise the uml diagram.


**NB:** One key takeaway is not to work in the same chat for a lot of prompts. AI starts to hallucinate especially when the tasks are not directly linked. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
