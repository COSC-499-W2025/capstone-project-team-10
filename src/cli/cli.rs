use std::sync::mpsc::Receiver;
use crate::core::msg::Msg;

pub fn start_cli(new_msg_queue: Receiver<Msg>) {
    let msg_queue = new_msg_queue;
    loop {
        let msg = msg_queue.recv().unwrap();
    }
}
