const user_bets_table = document.getElementById("user_bets_table")

function update_user_last_bets(bet_data, win)
{
    let user_bets_table_children = document.querySelectorAll("#user_bets_table > * ")
    let first_element = user_bets_table_children[0].cloneNode(true)

    let j = 0
    for(let i of first_element.children)
    {
        if(i.children.length==1)
        {
            let span_class = (win===0) ? "'text-danger'>" : "'text-success'>"
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
