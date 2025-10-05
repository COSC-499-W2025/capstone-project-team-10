use crate::types::mids::MID;
use std::collections::HashMap;
pub mod MSG {

    pub struct Msg {
        mid: MID,
        length: u32,
        data: Vec<u8>,
    }
    // MsgQueue stores receivers for subscriptions
    pub struct MsgQueue {
        queue: HashMap<MID, Receiver<Msg>>,
    }

    pub static mut TRANSCEIVERS: Option<HashMap<MID, (Sender<Msg>, Receiver<Msg>)>> = None;

    pub fn msgInit() {
        // Make a transmitter for each mid
        for mid in (0..MID_COUNT) {
            let (tx, rx) = channel();
            transceivers.insert(mid.clone(), (tx, rx));
        }
    }

    pub fn msgSubscribe(subscriber: MsgQueue, mid: MID) {}
    pub fn msgUnsubscribe(subscriber: MsgQueue, mid: MID) {}

    pub fn msgPost(msg: Msg, mid: MID) {}
    pub fn msgWait() {}
}
