const bet_coins = document.getElementsByName("bet_money")[0]
const percent_slider = document.getElementsByName("percent_to_win")[0]
const percent_label = document.getElementById("percent_label")
const multiplier_label = document.getElementById("multiplier_label")
const bet_form = document.getElementById("bet")

function multiply(){
    bet_coins.value *= 2
    multiplier_label.innerHTML = parseFloat(((bet_coins.value / (percent_slider.value / 100)) - bet_coins.value) * 0.99).toFixed(2)
}

function divide(){
    bet_coins.value /= 2
    multiplier_label.innerHTML = parseFloat(((bet_coins.value / (percent_slider.value / 100)) - bet_coins.value) * 0.99).toFixed(2)
}

function max(){
    let confirm = window.confirm("Czy chcesz zabetować wszystkimi dogami?")
    if(confirm)
    {
        bet_coins.value = user_money.textContent
        multiplier_label.innerHTML = parseFloat(((bet_coins.value / (percent_slider.value / 100)) - bet_coins.value) * 0.99).toFixed(2)
    }
}

percent_slider.oninput = function(){
    percent_label.innerHTML = this.value + "%"
}

bet_form.oninput = function(){
    multiplier_label.innerHTML = parseFloat(((bet_coins.value / (percent_slider.value / 100)) - bet_coins.value) * 0.99).toFixed(2)
}
