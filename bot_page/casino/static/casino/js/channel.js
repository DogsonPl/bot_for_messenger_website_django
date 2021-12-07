const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"
const socket = new WebSocket(ws_scheme + '://' + window.location.host + "/ws/casino/")

socket.onmessage = function(event){
    let bet_info = JSON.parse(event.data)
    let bet_info_ = bet_info["bet_info"]
    let win = bet_info["win"]
    update_last_bets(bet_info_, win)
}