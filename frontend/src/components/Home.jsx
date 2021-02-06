import React, { Component } from 'react';
import axios from 'axios'

class Home extends Component {	
    constructor(props) {
        super(props)
    
        this.state = {
					body: '',
					results: []
				}
		}
	
    handleChange =(event) => {
        this.setState({ body: event.target.value })
		}
		
		handleSubmit = (event) => {
			event.preventDefault(); // Avoid page refresh
			
			axios.post('/?max_n=5', this.state)
			.then(response => {
				console.log(response.data)
				this.setState( { results: response.data})
				console.log(this.state.results)
			})
			.catch(error => {
				console.log(error)
			})
		}
    
    render() {
        const {body, results} = this.state
            return (
                <div style={{display: 'flex',  justifyContent:'center', alignItems:'center', height: '100vh'}}>
                    <form onSubmit={this.handleSubmit}>
                      <div>
												<input 
												type="text" 
                          name="body" 
                          value={body} 
                          onChange={this.handleChange}/>
                    	</div>
                    
											<button type="submit">NANUDA</button>
											<br></br>
											<div>
											<br></br>
											{results.map(result => (
											
												<div >  
													<div>{result}</div>
													{/* <div>{result.emoji}</div> */}
													{/* <div>{result.confidence}</div> */}
												</div>
											))}
										</div>
                    </form>
                </div>
            )
    }
}

export default Home