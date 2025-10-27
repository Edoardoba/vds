import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  User, 
  Shield, 
  Bell, 
  Database, 
  Palette,
  Save,
  AlertTriangle,
  Key,
  Globe,
  Moon,
  Sun
} from 'lucide-react'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile')
  const [darkMode, setDarkMode] = useState(false)
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    uploads: true,
    analytics: false
  })

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'data', name: 'Data & Storage', icon: Database },
    { id: 'appearance', name: 'Appearance', icon: Palette },
  ]

  const handleSave = () => {
    // Save settings logic here
    console.log('Settings saved')
  }

  return (
    <div className="p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">
          Manage your account preferences and application settings
        </p>
      </motion.div>

      <div className="flex gap-6">
        {/* Settings Navigation */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-64 flex-shrink-0"
        >
          <div className="card p-0">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {tab.name}
                  </button>
                )
              })}
            </nav>
          </div>
        </motion.div>

        {/* Settings Content */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex-1"
        >
          <div className="card">
            {activeTab === 'profile' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Profile Settings</h3>
                
                <div className="space-y-6">
                  <div className="flex items-center gap-6">
                    <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                      <User className="w-8 h-8 text-primary-600" />
                    </div>
                    <div>
                      <button className="btn-secondary mb-2">Change Avatar</button>
                      <p className="text-sm text-gray-500">JPG, PNG or GIF. Max size of 5MB</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        defaultValue="John Doe"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email Address
                      </label>
                      <input
                        type="email"
                        className="input-field"
                        defaultValue="john@example.com"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Organization
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        defaultValue="Banta Analytics"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Role
                      </label>
                      <select className="input-field">
                        <option>Data Analyst</option>
                        <option>Data Scientist</option>
                        <option>Administrator</option>
                        <option>Viewer</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Security Settings</h3>
                
                <div className="space-y-6">
                  <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-5 h-5 text-yellow-600" />
                      <span className="font-medium text-yellow-800">Password Security</span>
                    </div>
                    <p className="text-sm text-yellow-700">
                      Last password change: 3 months ago. We recommend changing your password regularly.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <button className="flex items-center gap-3 p-4 w-full text-left border border-gray-200 rounded-lg hover:bg-gray-50">
                      <Key className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="font-medium text-gray-900">Change Password</p>
                        <p className="text-sm text-gray-500">Update your account password</p>
                      </div>
                    </button>

                    <button className="flex items-center gap-3 p-4 w-full text-left border border-gray-200 rounded-lg hover:bg-gray-50">
                      <Shield className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                        <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
                      </div>
                    </button>

                    <button className="flex items-center gap-3 p-4 w-full text-left border border-gray-200 rounded-lg hover:bg-gray-50">
                      <Globe className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="font-medium text-gray-900">API Keys</p>
                        <p className="text-sm text-gray-500">Manage API access keys</p>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Notification Preferences</h3>
                
                <div className="space-y-6">
                  {[
                    { key: 'email', label: 'Email Notifications', description: 'Receive notifications via email' },
                    { key: 'push', label: 'Push Notifications', description: 'Receive browser push notifications' },
                    { key: 'uploads', label: 'Upload Notifications', description: 'Notify when file uploads complete' },
                    { key: 'analytics', label: 'Analytics Reports', description: 'Weekly analytics summaries' },
                  ].map((item) => (
                    <div key={item.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{item.label}</p>
                        <p className="text-sm text-gray-500">{item.description}</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={notifications[item.key]}
                          onChange={(e) => setNotifications(prev => ({
                            ...prev,
                            [item.key]: e.target.checked
                          }))}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'data' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Data & Storage</h3>
                
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { label: 'Total Storage Used', value: '2.4 GB', max: '50 GB' },
                      { label: 'Files Uploaded', value: '127', max: '∞' },
                      { label: 'API Requests', value: '1.2K', max: '10K/month' },
                    ].map((stat) => (
                      <div key={stat.label} className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600">{stat.label}</p>
                        <p className="text-xl font-semibold text-gray-900">{stat.value}</p>
                        <p className="text-xs text-gray-500">of {stat.max}</p>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-4">
                    <button className="flex items-center gap-3 p-4 w-full text-left border border-gray-200 rounded-lg hover:bg-gray-50">
                      <Database className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="font-medium text-gray-900">Export Data</p>
                        <p className="text-sm text-gray-500">Download all your uploaded data</p>
                      </div>
                    </button>

                    <button className="flex items-center gap-3 p-4 w-full text-left border border-red-200 rounded-lg hover:bg-red-50 text-red-600">
                      <AlertTriangle className="w-5 h-5" />
                      <div>
                        <p className="font-medium">Delete All Data</p>
                        <p className="text-sm">Permanently remove all your data</p>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Appearance Settings</h3>
                
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      {darkMode ? <Moon className="w-5 h-5 text-gray-600" /> : <Sun className="w-5 h-5 text-gray-600" />}
                      <div>
                        <p className="font-medium text-gray-900">Dark Mode</p>
                        <p className="text-sm text-gray-500">Toggle dark mode interface</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={darkMode}
                        onChange={(e) => setDarkMode(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Theme Color
                    </label>
                    <div className="grid grid-cols-6 gap-3">
                      {['blue', 'green', 'purple', 'pink', 'orange', 'teal'].map((color) => (
                        <button
                          key={color}
                          className={`w-12 h-12 rounded-lg bg-${color}-500 hover:ring-2 hover:ring-${color}-300 transition-all`}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="flex justify-end mt-8 pt-6 border-t border-gray-200">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSave}
                className="btn-primary"
              >
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
