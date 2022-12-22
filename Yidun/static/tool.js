function B() {
    return "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx".replace(/[xy]/g, function (a) {
        var b = 16 * Math.random() | 0;
        return ("x" === a ? b : b & 3 | 8).toString(16)
    }).slice(2, 9) + '0'
}

function C() {
    return Math.random().toString(36).slice(2, 9)
}

console.log(Math.random().toString(36))
console.log(C())