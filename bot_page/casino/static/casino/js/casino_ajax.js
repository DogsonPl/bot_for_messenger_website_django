const user_money = document.getElementById("user_money")
const user_money_navbar = document.getElementById("user_money_navbar")
const daily_strike = document.getElementById("daily_strike")
const daily_button = document.getElementById("daily_button")
const bet_button = document.getElementById("bet_button")
const jackpot_button = document.getElementById("jackpot_button")
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
            if(status===0){
                let result = (response["win"]===1) ? "Wygrana" : "Przegrana"
                update_user_last_bets([response["date"], response["amount"], response["user_number"], response["drown_number"], result, parseFloat(response["money"]).toFixed(3)],
                                       response["win"])
                if(response["win"]===1){
                    bet_info_div.classList.add("alert-success")
                }
                else{
                    bet_info_div.classList.add("alert-danger")
                }
            }
            else{
                send_modal_message("Podano nieprawidłowe dane")
            }
            bet_info_div.hidden = false
            bet_info.innerHTML = response["message"]
            let user_money_formatted = parseFloat(response["player_money"]).toFixed(2)
            user_money.innerHTML = user_money_formatted
            user_money_navbar.innerHTML = user_money_formatted
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
            if(status===1){
                modal_message = "Nie masz wystarczająco pieniędzy"
            }
            else if(status===0){
                modal_message = "Kupiono " + response["tickets"] + " biletów"
            }
            send_modal_message(modal_message)
            let user_money_formatted = parseFloat(response["player_money"]).toFixed(2)
            user_money.innerHTML = user_money_formatted
            user_money_navbar.innerHTML = user_money_formatted
            total_tickets.innerHTML = parseInt(response["tickets"]) + parseInt(total_tickets.textContent)
            user_tickets.innerHTML = parseInt(response["tickets"]) + parseInt(user_tickets.textContent)
            jackpot_button.disabled = false
        },
        error: function(error){
            send_modal_message("Ups, nastąpił błąd po stronie serwera. Spróbuj ponownie później")
        },
        processData: false,
        contentType: false,
    })
})

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
