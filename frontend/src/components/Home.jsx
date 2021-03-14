import React, { Component } from "react";
import axios from "axios";
import { Button, TextField } from "@material-ui/core";
import Grid from "@material-ui/core/Grid";
import { Doughnut } from "react-chartjs-2";
import Typography from "@material-ui/core/Typography";
import Footer from "./Footer";
import "chartjs-plugin-labels";
import Alert from "@material-ui/lab/Alert";
import AlertTitle from "@material-ui/lab/AlertTitle";

/** Landing page to display emojis related to user inputted text */
class Home extends Component {
  // Max number of suggested characters
  max_chars = 140;
  constructor(props) {
    super(props);

    this.state = {
      tweet: "",
      results: [],
      chars_left: this.max_chars,
      backgroundColours: [],
      isShowingChart: false,
      noResults: false,
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

  // Called on text area change, dynamically update state of chars remaining in UI
  handleChange = (event) => {
    var input = event.target.value;
    // Clear UI for each net new search
    if (!input.length) {
      this.setState({
        results: [],
      });
    }

    this.setState({
      tweet: event.target.value,
      chars_left: this.max_chars - input.length,
      isShowingChart: false,
    });
  };

  // Pass input to BE and set state with results
  handleSubmit = (event) => {
    event.preventDefault();

    if (!this.state.tweet) {
      alert("Please type in a message to be classified!");
      return;
    }

    this.instance
      .post("/classify_text", {
        tweet: this.state.tweet,
      })
      .then((response) => {
        response.data.length
          ? this.setState({
              results: response.data,
              isShowingChart: true,
              noResults: false,
            })
          : this.setState({ noResults: true });
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
      temp += Math.floor((180 - temp) * random);
      result += temp.toString(16).padStart(2, "0");
    }
    return result;
  };

  generateRandomHexColour = () => {
    const randomColour = Math.floor(Math.random() * 16777215).toString(16);
    const hexValue = "#" + randomColour;
    return this.generateShades(hexValue);
  };

  getDonutColours(results) {
    const colours = [];
    for (var i = 0; i < results; i++) {
      colours.push(this.generateRandomHexColour());
    }
    return colours;
  }

  renderAlert() {
    return (
      <div>
        <Alert severity="error">
          <AlertTitle>Error</AlertTitle>
          Yeehaw, we we're unable to classify that. <br></br>
          <strong>Please try again with more descriptive words.</strong>
        </Alert>
      </div>
    );
  }
  renderChart(results) {
    var emojiArr = results.map(function (el) {
      return el.emoji;
    });
    var confArr = results.map(function (el) {
      return (el.confidence * 100).toFixed(2);
    });

    return (
      <div>
        <Doughnut
          data={{
            labels: emojiArr,
            datasets: [
              {
                data: confArr,
                backgroundColor: this.getDonutColours(results.length),
                borderWidth: 1,
              },
            ],
          }}
          height={400}
          width={600}
          options={{
            maintainAspectRatio: false,
            legend: {
              labels: {
                fontSize: 25,
                fontColor: "black",
              },
            },
          }}
        />
      </div>
    );
  }

  render() {
    require("./styles.css");
    const {
      results,
      backgroundColours,
      isShowingChart,
      noResults,
    } = this.state;
    const divStyle = {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "97vh",
      background: `linear-gradient(-45deg,${backgroundColours[0]},${backgroundColours[1]},
        ${backgroundColours[2]}, ${backgroundColours[3]}, ${backgroundColours[4]})`,
    };
    return (
      <div>
        <div style={divStyle}>
          <form>
            <Grid container spacing={5}>
              <Grid item xs={10}>
                <Typography variant="h1" align="left">
                  NANUDA
                </Typography>
                <Typography
                  style={{ width: 350 }}
                  variant="subtitle1"
                  align="left"
                >
                  Type in a message and get back emojis!
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  id="filled-multiline-static"
                  label="What are you thinking..."
                  multiline
                  rows={4}
                  className="textArea"
                  variant="filled"
                  onChange={this.handleChange}
                />
                <div
                  className="charsRemaining"
                  style={
                    this.state.chars_left >= 15
                      ? { color: "black" }
                      : { color: "red" }
                  }
                >
                  Characters Left: {this.state.chars_left}
                </div>

                <Button
                  type="submit"
                  variant="outlined"
                  style={{
                    backgroundColor: "white",
                    marginBottom: 10,
                    float: "right",
                  }}
                  onClick={(e) => this.handleSubmit(e)}
                >
                  Nanuda!
                </Button>
              </Grid>
              <Grid item xs={10}></Grid>
            </Grid>
            {isShowingChart && this.renderChart(results)}
            {noResults && this.renderAlert()}
          </form>
        </div>
        <Footer />
      </div>
    );
  }
}

export default Home;
