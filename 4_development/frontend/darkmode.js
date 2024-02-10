import React, { useState } from 'react';
import { View, TouchableOpacity, StyleSheet } from 'react-native';

const App = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [transitionDuration, setTransitionDuration] = useState('0.5s');

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    setTransitionDuration('0.5s');
  };

  return (
    <View style={[styles.container, isDarkMode && styles.darkContainer]}>
      <TouchableOpacity
        style={[styles.switch, isDarkMode && styles.darkSwitch]}
        onPress={toggleDarkMode}
      >
        <View
          style={[
            styles.toggleButton,
            isDarkMode && styles.darkToggleButton,
            { transitionDuration },
          ]}
        />
      </TouchableOpacity>
    </View>
    
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    transitionProperty: 'background-color',
    transitionDuration: '0.5s',
  },
  darkContainer: {
    backgroundColor: '#232323',
  },
  switch: {
    width: 80,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#272626',
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'flex-end',
    padding: 20,
    top: '10%',
    left: '75%',
  },
  darkSwitch: {
    backgroundColor: '#fff',
  },
  toggleButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#fff',
    position: 'absolute',
    top: 5,
    left: 5,
    transitionProperty: 'transform, background-color, transition-duration',
  },
  darkToggleButton: {
    transform: [{ translateX: 40 }],
    backgroundColor: '#232323',
  },
});

export default App;
