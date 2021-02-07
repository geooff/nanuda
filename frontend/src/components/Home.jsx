import React, { Component } from "react";
import axios from "axios";
import {
  IconButton,
  Input,
  TableContainer,
  Paper,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Table,
  Button,
} from "@material-ui/core";

/** Given an user input, display related emojis and their confidence level */
class Home extends Component {
  constructor(props) {
    super(props);

    this.state = {
      body: "",
      results: [],
    };
  }

  /** Called on input change */
  handleChange = (event) => {
    this.setState({ body: event.target.value });
  };

  /** Called on submit click */
  handleSubmit = (event) => {
    event.preventDefault();

    axios
      .post("/?max_n=5", this.state)
      .then((response) => {
        let responseArray = response.data;
        var responseObj = responseArray.map(function (x) {
          return {
            emoji: x[0],
            confidence: x[1],
          };
        });
        this.setState({ results: responseObj });
      })
      .catch((error) => {
        console.log(error);
      });
  };

  render() {
    const { body, results } = this.state;
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
        <h1>NANUDA TITLE</h1>
        <br></br>
        <div>
          <form onSubmit={this.handleSubmit}>
            <div>
              <Input
                type="text"
                name="body"
                value={body}
                onChange={this.handleChange}
              />
              <Button type="submit" variant="outlined">
                Classify
              </Button>
            </div>

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
                            {result.confidence}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    ))}
                  </Table>
                </TableContainer>
              )}
            </div>
          </form>
        </div>
      </div>
    );
  }
}

export default Home;
