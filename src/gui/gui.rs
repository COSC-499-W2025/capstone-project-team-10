use eframe::egui;
use std::sync::mpsc::Receiver;
use crate::core::msg::Msg;
struct gui {
    subscribers:
}
pub fn start_gui(new_msg_queue: Receiver<Msg>){
    let msg_queue = new_msg_queue;
    eframe::run_native(
        "My egui App",
        eframe::NativeOptions::default(),
        Box::new(|_cc| Ok(Box::new(MyApp::default()))),
    );
    /*loop
    {
        let msg = msg_queue.recv().unwrap();
    }*/
}

#[derive(Default)]
struct MyApp {}

impl eframe::App for MyApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.label("Hello, egui!");
            if ui.button("Click me!").clicked() {searchStartButton()}
        });
    }
}

static fn searchStartButton(){

}
