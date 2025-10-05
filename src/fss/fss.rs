use std::sync::mpsc::Receiver;
use crate::core::msg::Msg;
use crate::core::mids::MID;


static fn processMsg(Msg msg){
    match msg.mid {
        MID::MID_SEARCH_QUEUE => println!("Received Search start message"),
        _ => println!("Invalid Message Received"),
    }
}

pub fn start_fss(new_msg_queue: Receiver<Msg>) {
    let msg_queue = new_msg_queue;
    loop {
        print!("hoi");
        let msg = msg_queue.recv().unwrap();
        processMsg(msg);
    }
}
