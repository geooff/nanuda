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
} from "@material-ui/core";
import Grid from "@material-ui/core/Grid";

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
    };
  }

  instance = axios.create({
    baseURL: "http://api.nanuda.ca",
  });

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
      alert("Need text");
      return;
    }

    this.instance
      .post("/classify_text", {
        body: this.state.body,
      })
      .then((response) => {
        this.setState({ results: response.data });
      })
      .catch((error) => {
        console.log(error.response.data);
      });
  };

  render() {
    require("./styles.css");
    const { results } = this.state;
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          background:
            "linear-gradient(-45deg, #a1adc9, #637fc2, #1e46a6, #6e7085)",
        }}
      >
        <form onSubmit={this.handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <textarea
                className="textArea"
                onChange={this.handleChange.bind(this)}
              />
            </Grid>

            <Grid item xs={10}>
              <p
                className="charsRemaining"
                style={
                  this.state.chars_left >= 15
                    ? { color: "white", marginTop: -20 }
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
