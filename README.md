# Getting started

This plugin converts a string to template strings in following cases.
- When `${` is typed:
```
// | - is the cursor
let x = 'Hello, ${|'
let x = `Hello, ${|}`

// in JSX
const p = <p class="Hello, ${|"></p>
const p = <p class={"Hello, ${}"}></p>
```

- When entering a new line in empty string like `""` or `''` :
```
let x = '|'
let x = `
|
`

// in JSX  it is valid to have new lines in strings in JSX
const p = <p class="|"></p>
const p = <p class="
|
"></p>

// When you add a `${`
// only then will the string be converted to a template string
const p = <p class="
	${|
"></p>
const p = <p class={`
	${|}
`}></p>
```
