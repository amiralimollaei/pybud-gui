use pyo3::prelude::*;

use crate::ansi::string::AnsiString;
use crate::ansi::ColorMode;

use super::AnsiColor;

#[derive(Clone, Copy)]
struct Size {
    height: usize,
    width: usize
}

#[derive(Clone)]
#[pyclass]
pub struct Drawer {
    size: Size,
    #[pyo3(get, set)]
    plane: Vec<AnsiString>,
    #[pyo3(get, set)]
    plane_color: Option<(u8, u8, u8)>,
}

fn get_string_with_len(len: usize) -> String {
    " ".repeat(len).to_string()
}

fn get_char_with_len(char: char, len: usize) -> String {
    char.to_string().repeat(len).to_string()
}

// non-python methods
impl Drawer {
    fn check_write_position(&self, pos: (usize, usize)) -> bool{
        //assert!(pos.0 <= self.size.height);
        //assert!(pos.1 <= self.size.width);
        (pos.0 >= self.size.height) || (pos.1 >= self.size.width)
    }
}

fn make_empty_plane(height: usize, width: usize, color: Option<(u8, u8, u8)>) ->  Vec<AnsiString> {
    let mut plane: Vec<AnsiString> = Vec::with_capacity(height);
    for _ in 0..height {
        let blank_str = get_string_with_len(width);
        plane.push(match color {
            None => {AnsiString::new_colorless(blank_str.as_str())}
            Some(color) => {AnsiString::new_back(blank_str.as_str(), color)}
        });
    }
    plane
}

// python methods
#[pymethods]
impl Drawer {
    #[new]
    #[pyo3(signature = (width, height, plane_color=None))]
    #[inline]
    pub fn new(width: usize, height: usize, plane_color: Option<(u8, u8, u8)>) -> Drawer {
        Drawer {
            size: Size {
                width: width,
                height: height,
            },
            plane: make_empty_plane(height, width, plane_color),
            plane_color: plane_color
        }
    }

    #[pyo3(signature = (color=None))]
    pub fn fill(&mut self, color: Option<(u8, u8, u8)>) {
        self.plane = make_empty_plane(self.size.height, self.size.width, color)
    }

    pub fn clear(&mut self) {
        self.plane = make_empty_plane(self.size.height, self.size.width, self.plane_color)
    }

    pub fn render(&self, mode: &ColorMode) -> String {
        assert!(self.plane.len() > 0);
        let mut _render = String::with_capacity(self.size.width * self.size.height);
        for p in &self.plane {
            _render.push_str((p.to_string(mode) + "\n").as_str())
        }
        _render
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String{
        self.render(&ColorMode::TRUECOLOR)
    }

    pub fn place(&mut self, astr: &AnsiString, pos: (usize, usize), assign: bool) {
        if self.check_write_position(pos) {
            return
        }

        let write_len = astr.len();
        let end_idx = pos.1 + write_len;

        if end_idx > self.size.width {
            let mut _ansi_string = astr.clone();
            _ansi_string = _ansi_string.cut_at(write_len - (end_idx - self.size.width));
            self.plane[pos.0].place(&_ansi_string, pos.1, assign);
        } else {
            self.plane[pos.0].place(&astr, pos.1, assign);
        }
    }

    pub fn center_place(&mut self, astr: &AnsiString, ypos: usize, assign: bool) {
        let xpos: usize = (self.size.width - astr.len()) / 2;
        self.place(astr, (ypos, xpos), assign);
    }

    pub fn place_str(&mut self, _str: &str, pos: (usize, usize)) {
        // checks if we can write, and if index is out of bounds, returns
        if self.check_write_position(pos) {
            return
        }

        let write_len = _str.len();
        let end_idx = pos.1 + write_len;

        if end_idx > self.size.width {
            let _string = _str.split_at(write_len - (end_idx - self.size.width)).0;
            self.plane[pos.0].place_str(_string, pos.1);
        } else {
            self.plane[pos.0].place_str(_str, pos.1);
        }
    }

    pub fn center_place_str(&mut self, str: &str, ypos: usize) {
        let xpos: usize = (self.size.width - str.len()) / 2;
        self.place_str(str, (ypos, xpos));
    }

    pub fn place_drawer(&mut self, other: &Self, pos: (usize, usize), opacity: f32, border: bool, title: String) {
        if self.check_write_position(pos) {
            return
        }

        let mut other_mod = other.clone();

        for i in pos.0..self.size.height {
            // reletive height
            let rh: usize = i - pos.0;

            if rh > (other.size.height - 1) {
                break;
            }

            // other.plane's reletive line
            let otprl = &mut other_mod.plane[rh];

            if opacity != 1.0 {
                for i in 0..other_mod.size.width {
                    match otprl.vec[i].back_color {
                        None => {},
                        Some(bc) => {
                            otprl.vec[i].back_color = Some(AnsiColor {
                            0: (bc.0 as f32 * opacity) as u8,
                            1: (bc.1 as f32 * opacity) as u8,
                            2: (bc.2 as f32 * opacity) as u8,
                            });}
                    }
                }
            }

            if border {
                if rh == 0 {
                    let topbar_formatted = format!(
                        "┌┤{}├{}┐",
                        title,
                        get_char_with_len('─', other.size.width - title.len() -4)
                    );
                    otprl.place_str(topbar_formatted.as_str(), 0);
                } else if rh == (other.size.height - 1) {
                    let bottombar_formatted = format!(
                        "└{}┘",
                        get_char_with_len('─', other.size.width - 2)
                    );
                    otprl.place_str(bottombar_formatted.as_str(), 0);
                } else {
                    otprl.place_str("│", 0);
                    otprl.place_str("│", otprl.len()-1);
                }
            }

            self.plane[i].place(&otprl, pos.1, false);
            
        }
    }
}