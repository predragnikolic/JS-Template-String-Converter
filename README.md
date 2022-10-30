# Getting started

![example](./images/output1.gif)

This plugin converts a string to template strings in following cases.
- When `${` is typed:
```jsx
// | - is the cursor
let x = 'Hello, ${|'
let x = `Hello, ${|}`

// in JSX
const p = <p class="Hello, ${|"></p>
const p = <p class={"Hello, ${}"}></p>
```

Press `undo`, to undo the conversion if you do not want template strings.
```jsx
let x = 'Hello, ${|'
let x = `Hello, ${|}` // press undo
let x = "Hello, ${|}"
```

> This plugin is inspired by [Template String Converter](https://marketplace.visualstudio.com/items?itemName=meganrogge.template-string-converter) by  Megan Rogge.
