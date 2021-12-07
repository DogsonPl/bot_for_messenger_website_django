const user_bets_table = document.getElementById("user_bets_table")
const bets_table = document.getElementById("bets_table")

function update_user_last_bets(bet_data, win)
{
    let user_bets_table_children = document.querySelectorAll("#user_bets_table > * ")
    let first_element = user_bets_table_children[0].cloneNode(true)

    let j = 0
    for(let i of first_element.children)
    {
        if(i.children.length==1)
        {
            let span_class = (win==0) ? "'text-danger'>" : "'text-success'>"
            i.innerHTML = "<span class=" + span_class + bet_data[j] + " </span>"
        }
        else
        {
            i.innerHTML = bet_data[j]
        }
        j++
    }

    user_bets_table.insertAdjacentElement("afterbegin", first_element)
    if(user_bets_table_children.length == 10)
    {
        user_bets_table.removeChild(user_bets_table.lastElementChild)
    }
}


function update_last_bets(bet_data, win){
    let bets_table_children = document.querySelectorAll("#bets_table > * ")
    let first_element = bets_table_children[0].cloneNode(true)
    let j = 0
    for(let i of first_element.children)
    {
        if(j==4)
        {
            let span_class_text = (win==0) ? ["'text-danger'>", "Przegrana"] : ["'text-success'>", "Wygrana"]
            i.innerHTML = "<span class=" + span_class_text[0] + span_class_text[1] + " </span>"
        }
        else if(j==5)
        {
            let span_class = (win==0) ? "'text-danger'>" : "'text-success'>"
            i.innerHTML = "<span class=" + span_class + bet_data[j] + " </span>"
        }
        else
        {
            i.innerHTML = bet_data[j]
        }
        j++
    }

    bets_table.insertAdjacentElement("afterbegin", first_element)
    if(bets_table_children.length == 10)
    {
        bets_table.removeChild(bets_table.lastElementChild)
    }
}
