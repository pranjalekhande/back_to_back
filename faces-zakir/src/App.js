import './App.css';

function App() {
  return (
    <div className="App">
      <div className="faces-container">
        <div className="face-column">
          <img src="/head-1.png" className="head-image" alt="Head 1" />
          <img src="/mouth-1.png" className="mouth-image" alt="Mouth 1" />
        </div>
        <div className="face-column">
          <img src="/head-2.png" className="head-image" alt="Head 2" />
          <img src="/mouth-2.png" className="mouth-image" alt="Mouth 2" />
        </div>
      </div>
    </div>
  );
}

export default App;
