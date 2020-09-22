import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import CoursePage from './components/Course';
import QuestionPage from './components/Question';
import QuizPage from './components/Quiz';
import SessionPage from './components/Session';
import { Navbar, NavbarBrand, Nav, NavItem, NavLink } from 'react-bootstrap';

import { useEffect, useState } from 'react';

//import ReactDOM from 'react-dom';
import {
  BrowserRouter as Router,
  Switch,
  Route
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
        setCourseList(newCourseList);
    };

    useEffect(() => {
        fetchCourseList();
    }, [])

	return (
		<Router>
        	<div style={{ ...mainStyle }}>
        	    <div style={{ background: '#608f9f', borderRadius: '5px' }}>
                    <Navbar bg="transparent" expand="lg">
                        <Nav>
                            <NavbarBrand href="/">Quizzer</NavbarBrand>
                            { courseList.map((courseName) =>
                                <>
                                <div style={{ borderLeft: '1px solid darkgray' }}></div>
                                <NavItem>
                                    <NavLink href={ "/courses/" + courseName } >{ courseName }</NavLink>
                                </NavItem>
                                </>
                            )}
                            <div style={{ borderLeft: '1px solid darkgray' }}></div>
                        </Nav>
                    </Navbar>
                </div>
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
