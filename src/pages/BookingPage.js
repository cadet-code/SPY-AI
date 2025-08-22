import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { 
  Calendar, 
  Clock, 
  User, 
  Mail, 
  Phone, 
  CreditCard,
  CheckCircle,
  ArrowLeft,
  Sparkles
} from 'lucide-react';
import axios from 'axios';

const BookingPage = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [services, setServices] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  
  // Form data
  const [formData, setFormData] = useState({
    service_name: '',
    appointment_date: null,
    appointment_time: '',
    client_name: '',
    client_email: '',
    client_phone: '',
    special_requests: ''
  });

  // Load services on component mount
  useEffect(() => {
    loadServices();
  }, []);

  // Load available slots when service and date are selected
  useEffect(() => {
    if (formData.service_name && formData.appointment_date) {
      loadAvailableSlots();
    }
  }, [formData.service_name, formData.appointment_date]);

  const loadServices = async () => {
    try {
      const response = await axios.get('/api/services');
      setServices(response.data);
    } catch (error) {
      console.error('Error loading services:', error);
      toast.error('Failed to load services');
    }
  };

  const loadAvailableSlots = async () => {
    try {
      const dateStr = formData.appointment_date.toISOString().split('T')[0];
      const response = await axios.get(`/api/available-slots?date=${dateStr}&service_name=${formData.service_name}`);
      setAvailableSlots(response.data.available_slots);
    } catch (error) {
      console.error('Error loading available slots:', error);
      toast.error('Failed to load available time slots');
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const bookingData = {
        ...formData,
        appointment_date: formData.appointment_date.toISOString().split('T')[0]
      };

      const response = await axios.post('/api/book', bookingData);
      
      toast.success('Booking confirmed! Check your email for details.');
      
      // Reset form
      setFormData({
        service_name: '',
        appointment_date: null,
        appointment_time: '',
        client_name: '',
        client_email: '',
        client_phone: '',
        special_requests: ''
      });
      setStep(1);
      
    } catch (error) {
      console.error('Booking error:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to create booking';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const canProceedToStep2 = formData.service_name && formData.appointment_date && formData.appointment_time;
  const canProceedToStep3 = formData.client_name && formData.client_email && formData.client_phone;

  const selectedService = services.find(s => s.name === formData.service_name);

  return (
    <div className="pt-16 min-h-screen gradient-bg">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Sparkles className="h-8 w-8 text-spa-500" />
            <h1 className="text-4xl font-bold text-gray-900">Book Your Spa Experience</h1>
          </div>
          <p className="text-xl text-gray-600">
            Choose your service, pick a time, and let our AI handle the rest
          </p>
        </motion.div>

        {/* Progress Steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex justify-center mb-8"
        >
          <div className="flex items-center space-x-4">
            {[1, 2, 3].map((stepNumber) => (
              <div key={stepNumber} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  step >= stepNumber 
                    ? 'bg-spa-500 border-spa-500 text-white' 
                    : 'border-gray-300 text-gray-500'
                }`}>
                  {step > stepNumber ? (
                    <CheckCircle className="h-6 w-6" />
                  ) : (
                    <span className="font-semibold">{stepNumber}</span>
                  )}
                </div>
                {stepNumber < 3 && (
                  <div className={`w-16 h-0.5 mx-2 ${
                    step > stepNumber ? 'bg-spa-500' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Booking Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Step 1: Service Selection */}
            {step === 1 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <div>
                  <h2 className="text-2xl font-semibold text-gray-900 mb-4 flex items-center">
                    <Calendar className="h-6 w-6 mr-2 text-spa-500" />
                    Choose Your Service
                  </h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {services.map((service) => (
                      <motion.div
                        key={service.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-300 ${
                          formData.service_name === service.name
                            ? 'border-spa-500 bg-spa-50'
                            : 'border-gray-200 hover:border-spa-300'
                        }`}
                        onClick={() => handleInputChange('service_name', service.name)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-semibold text-gray-900">{service.name}</h3>
                          <span className="text-lg font-bold text-spa-600">${service.price}</span>
                        </div>
                        <p className="text-gray-600 text-sm mb-2">{service.description}</p>
                        <div className="flex items-center text-sm text-gray-500">
                          <Clock className="h-4 w-4 mr-1" />
                          {service.duration} minutes
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {formData.service_name && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                  >
                    <h3 className="text-lg font-semibold text-gray-900">Select Date & Time</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Appointment Date
                        </label>
                        <DatePicker
                          selected={formData.appointment_date}
                          onChange={(date) => handleInputChange('appointment_date', date)}
                          minDate={new Date()}
                          filterDate={(date) => date.getDay() !== 0} // No Sundays
                          className="input-field"
                          placeholderText="Select date"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Appointment Time
                        </label>
                        <select
                          value={formData.appointment_time}
                          onChange={(e) => handleInputChange('appointment_time', e.target.value)}
                          className="input-field"
                          disabled={!formData.appointment_date}
                        >
                          <option value="">Select time</option>
                          {availableSlots.map((slot) => (
                            <option key={slot} value={slot}>{slot}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </motion.div>
                )}

                <div className="flex justify-end">
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={!canProceedToStep2}
                    className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                      canProceedToStep2
                        ? 'btn-primary'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                    onClick={() => setStep(2)}
                  >
                    Continue
                  </motion.button>
                </div>
              </motion.div>
            )}

            {/* Step 2: Personal Information */}
            {step === 2 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
                    <User className="h-6 w-6 mr-2 text-spa-500" />
                    Your Information
                  </h2>
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex items-center space-x-2 text-spa-600 hover:text-spa-700"
                    onClick={() => setStep(1)}
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span>Back</span>
                  </motion.button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      value={formData.client_name}
                      onChange={(e) => handleInputChange('client_name', e.target.value)}
                      className="input-field"
                      placeholder="Enter your full name"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={formData.client_email}
                      onChange={(e) => handleInputChange('client_email', e.target.value)}
                      className="input-field"
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={formData.client_phone}
                      onChange={(e) => handleInputChange('client_phone', e.target.value)}
                      className="input-field"
                      placeholder="Enter your phone number"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Special Requests (Optional)
                  </label>
                  <textarea
                    value={formData.special_requests}
                    onChange={(e) => handleInputChange('special_requests', e.target.value)}
                    className="input-field"
                    rows="3"
                    placeholder="Any special requests or notes..."
                  />
                </div>

                <div className="flex justify-between">
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="btn-secondary"
                    onClick={() => setStep(1)}
                  >
                    Back
                  </motion.button>
                  
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={!canProceedToStep3}
                    className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                      canProceedToStep3
                        ? 'btn-primary'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                    onClick={() => setStep(3)}
                  >
                    Continue
                  </motion.button>
                </div>
              </motion.div>
            )}

            {/* Step 3: Review & Confirm */}
            {step === 3 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
                    <CreditCard className="h-6 w-6 mr-2 text-spa-500" />
                    Review & Confirm
                  </h2>
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex items-center space-x-2 text-spa-600 hover:text-spa-700"
                    onClick={() => setStep(2)}
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span>Back</span>
                  </motion.button>
                </div>

                <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Booking Summary</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-900">Service Details</h4>
                      <p className="text-gray-600">{selectedService?.name}</p>
                      <p className="text-gray-600">{selectedService?.duration} minutes</p>
                      <p className="text-gray-600">${selectedService?.price}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900">Appointment</h4>
                      <p className="text-gray-600">
                        {formData.appointment_date?.toLocaleDateString()}
                      </p>
                      <p className="text-gray-600">{formData.appointment_time}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900">Contact Information</h4>
                      <p className="text-gray-600">{formData.client_name}</p>
                      <p className="text-gray-600">{formData.client_email}</p>
                      <p className="text-gray-600">{formData.client_phone}</p>
                    </div>
                  </div>

                  {formData.special_requests && (
                    <div>
                      <h4 className="font-medium text-gray-900">Special Requests</h4>
                      <p className="text-gray-600">{formData.special_requests}</p>
                    </div>
                  )}
                </div>

                <div className="flex justify-between">
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="btn-secondary"
                    onClick={() => setStep(2)}
                  >
                    Back
                  </motion.button>
                  
                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={loading}
                    className="btn-primary flex items-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-5 w-5" />
                        <span>Confirm Booking</span>
                      </>
                    )}
                  </motion.button>
                </div>
              </motion.div>
            )}
          </form>
        </motion.div>
      </div>
    </div>
  );
};

export default BookingPage;
