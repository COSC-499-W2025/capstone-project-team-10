use std::env;
use std::thread::{self, JoinHandle};
use std::sync::mpsc;
use crate::core::msg::MSG;
fn main()
{
    let args: Vec<String> = env::args().collect();
    // Message Structure
    let (ui_tx, ui_rx) = mpsc::channel::<Msg>();
    let (file_search_tx, file_search_rx) = mpsc::channel::<types::Msg>();
    let (file_analysis_tx, file_analysis_rx) = mpsc::channel::<types::Msg>();
    let (file_export_tx, file_export_rx) = mpsc::channel::<types::Msg>();



    // start tasks
    let mut fileSearchSubscribers: HashMap<String, Sender<Msg> = HashMap::new();
    fileSearchSubscribers.insert("file_analysis_tx".to_string(), file_analysis_tx)
    let _file_search_handle = thread::spawn(move || {fss::start_fss(file_search_rx, )});
    // TODO: Determine if the GUI or CLI is being used
    gui::start_gui(ui_rx, Vec<Tran)
}
