import React, { Component } from "react";
import axios from "axios";
import {
  TableContainer,
  Paper,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Table,
  Button,
  TextField,
} from "@material-ui/core";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import Slide from "@material-ui/core/Slide";
import Grid from "@material-ui/core/Grid";

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

/** Landing page to display emojis related to user inputted text */
class Home extends Component {
  // Max number of suggested characters
  max_chars = 140;
  constructor(props) {
    super(props);

    this.state = {
      body: "",
      results: [],
      chars_left: this.max_chars,
      backgroundColours: [],
      setOpen: false,
    };
  }
  componentDidMount() {
    const colours = [];
    const baseHex = this.generateRandomHexColour();
    for (var i = 0; i < 5; i++) {
      colours.push(this.generateShades(baseHex));
    }
    this.setState({ backgroundColours: colours });
  }

  instance = axios.create({
    baseURL: "http://api.nanuda.ca",
  });

  handleClickOpen = () => {
    this.setState({ setOpen: true });
  };

  handleClose = () => {
    this.setState({ setOpen: false });
  };
  // Called on text area change, dynamically update state of chars remaining in UI
  handleChange = (event) => {
    var input = event.target.value;
    this.setState({
      body: event.target.value,
      chars_left: this.max_chars - input.length,
    });
  };

  // Pass input to BE and set state with results
  handleSubmit = (event) => {
    event.preventDefault();
    if (!this.state.body) {
      alert("Need a message");
      return;
    }

    this.instance
      .post("/classify_text", {
        body: this.state.body,
      })
      .then((response) => {
        response.data.length
          ? this.setState({ results: response.data })
          : alert("Yeehaw, we didnt catch that. Please try again");
      })
      .catch((error) => {
        console.log(error.response.data);
      });
  };

  generateShades = (color) => {
    var p = 1,
      temp,
      random = Math.random(),
      result = "#";

    while (p < color.length) {
      temp = parseInt(color.slice(p, (p += 2)), 16);
      temp += Math.floor((255 - temp) * random);
      result += temp.toString(16).padStart(2, "0");
    }
    return result;
  };

  generateRandomHexColour = () => {
    const randomColour = Math.floor(Math.random() * 16777215).toString(16);
    const hexValue = "#" + randomColour;

    return this.generateShades(hexValue);
  };

  /**
   * TODO: Connect replace alerts with dialog
   */
  renderDialog() {
    const { setOpen } = this.state;
    return (
      <>
        <Dialog
          open={setOpen}
          TransitionComponent={Transition}
          keepMounted
          onClose={this.handleClose}
          aria-labelledby="alert-dialog-slide-title"
          aria-describedby="alert-dialog-slide-description"
        >
          <DialogTitle id="alert-dialog-slide-title">
            {"Yeehaw, we did not catch that"}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-slide-description">
              Pls try again with a better msg, ty.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={this.handleClose} color="primary">
              Nah
            </Button>
            <Button onClick={this.handleClose} color="primary">
              I Suppose
            </Button>
          </DialogActions>
        </Dialog>
      </>
    );
  }
  render() {
    require("./styles.css");
    const { results, backgroundColours } = this.state;
    const divStyle = {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      background: `linear-gradient(-45deg,${backgroundColours[0]},${backgroundColours[1]},
        ${backgroundColours[2]}, ${backgroundColours[3]}, ${backgroundColours[4]})`,
    };
    return (
      <div style={divStyle}>
        <form onSubmit={this.handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                id="filled-multiline-static"
                label="What are you thinking..."
                multiline
                rows={4}
                className="textArea"
                variant="filled"
                onChange={this.handleChange.bind(this)}
              />
            </Grid>

            <Grid item xs={10}>
              <p
                className="charsRemaining"
                style={
                  this.state.chars_left >= 15
                    ? { color: "black", marginTop: -20 }
                    : { color: "red", marginTop: -20 }
                }
              >
                Characters Left: {this.state.chars_left}
              </p>
            </Grid>
            <Grid item xs={2}>
              <Button
                type="submit"
                variant="outlined"
                style={{ backgroundColor: "white" }}
              >
                Classify
              </Button>
            </Grid>

            <Grid item xs={12}>
              <div>
                {results.length > 0 && (
                  <TableContainer component={Paper}>
                    <Table aria-label="simple-table">
                      <TableHead>
                        <TableRow>
                          <TableCell>Emoji</TableCell>
                          <TableCell align="right">Confidence</TableCell>
                        </TableRow>
                      </TableHead>
                      {results.map((result) => (
                        <TableBody>
                          <TableRow key={result.emoji}>
                            <TableCell component="th" scope="row">
                              {result.emoji}
                            </TableCell>
                            <TableCell align="right">
                              {(result.confidence * 100).toFixed(2)}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      ))}
                    </Table>
                  </TableContainer>
                )}
              </div>
            </Grid>
          </Grid>
        </form>
      </div>
    );
  }
}

export default Home;
