const user_money = document.getElementById("user_money")
const user_money_navbar = document.getElementById("user_money_navbar")
const daily_strike = document.getElementById("daily_strike")
const daily_button = document.getElementById("daily_button")
const bet_button = document.getElementById("bet_button")
const jackpot_button = document.getElementById("jackpot_button")
const scratch_button = document.getElementById("scratch_button")
const user_tickets = document.getElementById("user_tickets")
const total_tickets = document.getElementById("total_tickets")
const bet_info = document.getElementById("bet_info")
const bet_info_div = document.getElementById("bet_info_div")
const modal_message_box = document.getElementById("modal_info")

const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value
const form_percent_to_win = document.getElementsByName("percent_to_win")[0]
const form_bet_money = document.getElementsByName("bet_money")[0]
const jackpot_tickets_to_buy = document.getElementsByName("tickets")[0]


$("#daily_button").on("click", function(event){
    event.preventDefault()
    const daily_form_data = new FormData()
    daily_form_data.append('csrfmiddlewaretoken', csrf)
    $.ajax({
        type: 'POST',
        url: 'set_daily',
        data: daily_form_data,
        success: function(response){
            let user_money_formatted = parseFloat(response["player_money"]).toFixed(2)
            user_money.innerHTML = user_money_formatted
            user_money_navbar.innerHTML = user_money_formatted
            daily_strike.innerHTML = response["daily_strike"]
            send_modal_message(response["received"])
            daily_button.textContent = "Odebrano już dzisiaj daily"
            daily_button.disabled = true
        },
        error: function(error){
            send_modal_message("Ups, nastąpił błąd po stronie serwera. Spróbuj ponownie później")
        },
        processData: false,
        contentType: false,
    })
})

$("#bet").on("submit", function(event){
    bet_button.disabled = true
    event.preventDefault()
    const bet_form_data = new FormData()
    bet_form_data.append('csrfmiddlewaretoken', csrf)
    bet_form_data.append("percent_to_win", form_percent_to_win.value)
    bet_form_data.append("bet_money", form_bet_money.value)
    $.ajax({
        type: 'POST',
        url: 'bet',
        data: bet_form_data,
        success: function(response){
            let status = response["status"]
            bet_info_div.classList.remove("alert-success")
            bet_info_div.classList.remove("alert-danger")
            if(status==0){
                let result = (response["win"]==1) ? "Wygrana" : "Przegrana"
                update_user_last_bets([response["date"], response["amount"], response["user_number"], response["drown_number"], result, parseFloat(response["money"]).toFixed(3)],
                                       response["win"])
                if(response["win"]==1){
                    bet_info_div.classList.add("alert-success")
                }
                else{
                    bet_info_div.classList.add("alert-danger")
                    if(response["player_money"] < bet_coins.value){
                        bet_coins.value = 0
                        update_multiplier_label()
                    }
                }
                let user_money_formatted = parseFloat(response["player_money"]).toFixed(2)
                user_money.innerHTML = user_money_formatted
                user_money_navbar.innerHTML = user_money_formatted
            }
            else{
                send_modal_message("Podano nieprawidłowe dane")
            }
            bet_info.innerHTML = response["message"]
            bet_button.disabled = false
        },
        error: function(error){
            send_modal_message("Ups, nastąpił błąd po stronie serwera. Spróbuj ponownie później")
        },
        processData: false,
        contentType: false,
    })
})

$("#jackpot").on("submit", function(event){
    jackpot_button.disabled = true
    event.preventDefault()
    const jackpot_form_data = new FormData()
    jackpot_form_data.append('csrfmiddlewaretoken', csrf)
    jackpot_form_data.append("tickets", jackpot_tickets_to_buy.value)
    $.ajax({
        type: 'POST',
        url: 'jackpot_buy',
        data: jackpot_form_data,
        success: function(response){
            let status = response["status"]
            let modal_message = ""
            if(status==1){
                modal_message = "Nie masz wystarczająco pieniędzy"
            }
            else if(status==0){
                modal_message = "Kupiono " + response["tickets"] + " biletów"
                let user_money_formatted = parseFloat(response["player_money"])
                user_money.innerHTML = user_money_formatted
                user_money_navbar.innerHTML = user_money_formatted
                total_tickets.innerHTML = parseInt(response["tickets"]) + parseInt(total_tickets.textContent)
                user_tickets.innerHTML = parseInt(response["tickets"]) + parseInt(user_tickets.textContent)
            }
            else if(status==2){
                modal_message = "💤 Obecnie trwa losowanie, spróbuj za kilka sekund"
            }
            send_modal_message(modal_message)
            jackpot_button.disabled = false
        },
        error: function(error){
            send_modal_message("Ups, nastąpił błąd po stronie serwera. Spróbuj ponownie później")
        },
        processData: false,
        contentType: false,
    })
})

$("#scratch_button").on("click", function(event){
    event.preventDefault()
    const data = new FormData()
    data.append('csrfmiddlewaretoken', csrf)
    $.ajax({
        type: 'POST',
        url: 'buy_scratch_card',
        data: data,
        success: function(response){
            send_modal_message(response["message"])
            if(response["message"]!="🚫 Nie masz wystarczająco dogecoinów by kupić zdrapke, koszt zdrapki to 5 dogecoinów"){
                player_money = response["player_money"]
                user_money.innerHTML = player_money
                user_money_navbar.innerHTML = player_money
                scratch_button.disabled = true
                if(response["scratch_boost"]){
                    scratch_timeout = "9:59"
                }
                else{
                    scratch_timeout = "19:59"
                }
                scratch_timeout_p.innerHTML = "Możesz odebrać zdrapke za " + scratch_timeout + " minut"
                var scratch_timer = setInterval(update_scratch_timeout, 1000, [scratch_timeout])
            }
        },
        error: function(error){
            send_modal_message("Ups, nastąpił błąd po stronie serwera. Spróbuj ponownie później")
        },
        processData: false,
        contentType: false,
    })
})


function shop(button){
    const data = new FormData()
    data.append('csrfmiddlewaretoken', csrf)
    data.append("item_id", button.value)
    $.ajax({
        type: 'POST',
        url: 'shop',
        data: data,
        success: function(response){
            if(response["bought"]){
                location.reload()
            }
            else{
                send_modal_message(response["message"])
            }
        },
        error: function(error){
            send_modal_message("Ups, nastąpił błąd po stronie serwera. Spróbuj ponownie później")
        },
        processData: false,
        contentType: false,
    })
}


function send_modal_message(message){
    $.notify({
        icon: "bi bi-bell",
        message: message
    },
    {
        type: "success",
        timer: 1000,
        placement: { from: "top", align: "right"}
    });
}
