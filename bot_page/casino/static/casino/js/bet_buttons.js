const bet_coins = document.getElementsByName("bet_money")[0]
const percent_slider = document.getElementsByName("percent_to_win")[0]
const percent_label = document.getElementById("percent_label")
const multiplier_label = document.getElementById("multiplier_label")
const bet_form = document.getElementById("bet")

function multiply(){
    bet_coins.value *= 2
    update_multiplier_label()
}

function divide(){
    bet_coins.value /= 2
    update_multiplier_label()
}

function max(){
    let confirm = window.confirm("Czy chcesz zabetować wszystkimi dogami?")
    if(confirm)
    {
        bet_coins.value = user_money.textContent
        update_multiplier_label()
    }
}

percent_slider.oninput = function(){
    percent_label.innerHTML = this.value + "%"
}

bet_form.oninput = function(){
    update_multiplier_label()
}


function update_multiplier_label(){
    multiplier_label.innerHTML = parseFloat(((bet_coins.value / (percent_slider.value / 100)) - bet_coins.value) * 0.99).toFixed(2)
}
