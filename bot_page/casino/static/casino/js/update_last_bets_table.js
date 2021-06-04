const user_bets_table = document.querySelectorAll("#user_bets_table > * ")

function update_user_last_bets(bet_data, win)
{
    let table_data = []
    for(let col of user_bets_table)
    {
        table_data.push(col.innerHTML)
    }
    for(let i=1; i<user_bets_table.length-1; i++)
    {
        user_bets_table[i].innerHTML = table_data[i-1]
    }

    let j = 0
    for(let i of user_bets_table[0].children)
    {
        if(i.children.length===1)
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
}

