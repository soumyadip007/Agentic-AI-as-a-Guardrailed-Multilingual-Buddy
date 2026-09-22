# Loops

A **loop** repeats a block of code while a condition holds or over a sequence.

## For loops

- `for item in sequence:` iterates over each element
- `range(n)` yields `0 .. n-1`
- Example pattern: `for i in range(len(nums)):`

## While loops

- `while condition:` repeats until the condition is false
- Always ensure the loop variable changes, or you may infinite-loop

## Key tips

- Prefer `for` when the number of iterations is known from a sequence
- Use `break` to exit early; `continue` to skip to the next iteration
