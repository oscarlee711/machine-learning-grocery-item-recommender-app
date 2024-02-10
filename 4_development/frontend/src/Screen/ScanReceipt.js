import React, { useEffect, useState } from 'react';
import { useNavigation } from '@react-navigation/native';
import { View, Text, StyleSheet, Image, TouchableOpacity, ScrollView } from 'react-native';
import { useSelector } from 'react-redux';
import ImagePicker from 'react-native-image-crop-picker';
import axios from 'axios';
import api from '../core/Service';

const Setting = () => {
	const navigation = useNavigation();
	const token = useSelector(state => state.app.token);

	// Declaring state variables
	// useState allows for the tracking of a state in a fuctional component 
	// which is helpful for re-rendering and updating the application
	const [image, setImage] = useState(null);
	const [imageList, setImageList] = useState([]);

	// Add image into image list
	useEffect(() => {
		if (image) {
			setImageList([...imageList, image]);
			console.log(imageList);
		}
	}, [image]);

	// Open device camera and take image
	const takePhoto = async () => {
		try {
			// Set width and height restrictions here
			const { path, width, height, mime } = await ImagePicker.openCamera({
				width: 300,
				height: 400,
				cropping: false
			});
			setImage({ uri: path, width, height, mime });
		} catch (error) {
			console.log('Failed to take photo', error);
		}
	};

	// Open device gallery and select image
	const choosePhoto = async () => {
		try {
			// Set width and height restrictions here
			const { path, width, height, mime } = await ImagePicker.openPicker({
				width: 300,
				height: 400,
				cropping: false
			});
			setImage({ uri: path, width, height, mime });
		} catch (error) {
			console.log('Failed to choose photo', error);
		}
	};

	// Clear the selected image and the image list
	const cancelPhoto = () => {
		setImage(null);
		setImageList([]);
		console.log(imageList);
	};

	// Rendering single image
	// Added index to pass as unique key prop to allow for efficient updating of DOM
	const renderPhoto = (image, index) => (
		<View style={styles.photo_container} key={index}>
			<Image style={styles.photo} source={{ uri: image.uri }} />
		</View>
	)

	// Upload selected image to database server
	const submitPhoto = async () => {
		try {
			const bodyFormData = new FormData();
			bodyFormData.append('image', {
				uri: image.uri,
				type: 'image/jpeg',
				name: 'image.jpeg'
			});

			const headers = { 'Content-Type': 'multipart/form-data', 'Authorization': 'Bearer ' + token }
			await axios.post(`${api}/receipt`, bodyFormData, { headers: headers })
				.then(function (response) {
					console.warn('Upload successful');
					navigation.navigate('ReceiptResult')
					// Clear image aswell as image list
					setImage(null);
					setImageList([]);

					// Code to remove temporary files that may exist when an image is picked
					// This code removes cache files that may build up over extended use
					ImagePicker.clean().then(() => {
						console.log('removed all tmp images from tmp directory');
					}).catch(e => {
						alert(e);
					});
				})
				.catch(function (error) {
					setImage(null);
					setImageList([]);
					return;
				});
		} catch (error) {
		  console.warn('Upload failed, please try again', error);
		}
	}
	
	//Crop the image
	//Has rotate, crop and scale functionality
	const editImage = async () => {
		try {
			const { path, width, height, mime } = await ImagePicker.openCropper({
				path: image.uri
			});
			setImageList
			setImage(null);
			setImage({ uri: path, width, height, mime });
		} catch (error) {
			console.warn('Failed to crop image', error);
		}
	}

	// Cancel, Edit and Submit will only appear after an image has taken/selected
	return (
		<View style={styles.container}>
			<ScrollView>
				<Text style={styles.header}>Scan Receipt</Text>
				{image ?
					<View>
						{imageList.map((image, index => renderPhoto(image, index)))}
						<TouchableOpacity style={styles.cancelbtn} onPress={cancelPhoto}>
							<Text style={styles.btn_text}>Cancel</Text>
						</TouchableOpacity>
						<TouchableOpacity style={styles.btn} onPress={editImage}>
							<Text style={styles.btn_text}>Edit</Text>
						</TouchableOpacity>
						<TouchableOpacity style={styles.btn} onPress={submitPhoto}>
							<Text style={styles.btn_text}>Submit</Text>
						</TouchableOpacity>
					</View> :
					<View>
						<TouchableOpacity style={styles.btn} onPress={takePhoto}>
							<Text style={styles.btn_text}>Take a Photo</Text>
						</TouchableOpacity>
						<TouchableOpacity style={styles.btn} onPress={choosePhoto}>
							<Text style={styles.btn_text}>Choose from Photos</Text>
						</TouchableOpacity>
					</View>
				}
			</ScrollView>
		</View>
	)
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		marginTop: 17,
		paddingHorizontal: 32
	},
	header: {
		fontSize: 24,
		fontWeight: 'bold',
		color: 'black'
	},
	tab: {
		flexDirection: 'row',
		marginTop: 28,
		justifyContent: 'flex-start'
	},
	btn: {
		marginTop: 20,
		backgroundColor: '#4F44D0',
		borderRadius: 50,
		paddingVertical: 21
	},
	cancelbtn: {
		marginTop: 20,
		backgroundColor: '#4F44D0',
		paddingVertical: 10,
		marginHorizontal: 30
	},
		btn_text: {
		textAlign: 'center',
		color: 'white',
		fontSize: 15
	},
	activeTab: {
		color: 'black'
	},
	photo: {
		width: 400,
		height: 400,
		resizeMode: 'contain'
	},
	photo_container: {
		alignItems: 'center'
	}
});

export default Setting;