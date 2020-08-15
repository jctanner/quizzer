import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import CoursePage from './components/Course';
import QuestionPage from './components/Question';
import QuizPage from './components/Quiz';
import SessionPage from './components/Session';

import { useEffect, useState } from 'react';

//import ReactDOM from 'react-dom';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useParams
} from "react-router-dom";


var mainStyle = {
  background: "#eee",
  padding: "20px",
  margin: "20px"
};

function NotFound() {
    return <div>Not Found</div>
}

// HOME
function Home() {
	return (
		<div><h2>HOME</h2></div>
	)
};

function App() {

    const [ courseList, setCourseList ] = useState([]);

    const fetchCourseList = async () => {
        const newCourseList = await fetch('/api/courses')
            .then(res => res.json())
        console.log(typeof newCourseList);
        setCourseList(newCourseList);
    };

    useEffect(() => {
        fetchCourseList();
    }, [])

    console.log('cl type', typeof courseList);

	return (
		<Router>
        	<div style={ mainStyle }>
				<ul>
					<li>
						<Link key="home" to="/">Home</Link>
					</li>
            		{courseList.map((courseName) => 
                        <li key={courseName }>
					        <Link to={ "/courses/" + courseName }>{ courseName }</Link>
                        </li>
					)}
				</ul>
				<hr/>
				<Switch>
					<Route exact path="/" component={ Home } />
                    <Route path="/courses/:courseName/quiz" component={ QuizPage }/>
					<Route path="/courses/:courseName/questions/:questionId" component={ QuestionPage } />
					<Route path="/courses/:courseName" component={ CoursePage } />
					<Route path="/sessions/:sessionid" component={ SessionPage } />
                    <Route component={ NotFound } />
				</Switch>
			</div>
		</Router>
	);

}

export default App;
