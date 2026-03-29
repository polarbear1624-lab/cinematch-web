import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';

export default function AccountCenter({ user }) {
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('');
  const [bio, setBio] = useState('');

  // Fetch the user's existing profile data when the tab loads
  useEffect(() => {
    async function getProfile() {
      try {
        const { data, error } = await supabase
          .from('profiles')
          .select('username, bio')
          .eq('id', user.id)
          .single();

        if (data) {
          setUsername(data.username || '');
          setBio(data.bio || '');
        }
      } catch (error) {
        console.log("No profile found, creating a new one.");
      } finally {
        setLoading(false);
      }
    }

    if (user) getProfile();
  }, [user]);

  // Save the new data back to the database
  const updateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);

    const updates = {
      id: user.id,
      username,
      bio,
      updated_at: new Date(),
    };

    const { error } = await supabase.from('profiles').upsert(updates);

    if (error) {
      alert("Error updating profile: " + error.message);
    } else {
      alert("✨ Profile updated successfully!");
    }
    setLoading(false);
  };

  if (loading) return <div className="spinner" style={{ margin: '50px auto' }}></div>;

  return (
    <div className="account-center-container fade-in">
      <div className="auth-card" style={{ margin: '0 auto', marginTop: '20px' }}>
        <div className="empty-emoji" style={{ fontSize: '3rem', marginBottom: '10px' }}>👤</div>
        <h3 className="auth-title">Your Profile</h3>
        <p className="auth-subtitle">{user.email}</p>

        <form onSubmit={updateProfile} className="auth-form">
          <div style={{ textAlign: 'left' }}>
            <label style={{ color: '#94A3B8', fontSize: '12px', marginLeft: '5px' }}>Display Name</label>
            <input
              className="auth-input"
              style={{ width: '100%', boxSizing: 'border-box', marginTop: '5px' }}
              type="text"
              placeholder="e.g. CinemaKing99"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div style={{ textAlign: 'left', marginTop: '10px' }}>
            <label style={{ color: '#94A3B8', fontSize: '12px', marginLeft: '5px' }}>Favorite Movie / Bio</label>
            <textarea
              className="auth-input"
              style={{ width: '100%', boxSizing: 'border-box', marginTop: '5px', minHeight: '80px', resize: 'vertical' }}
              placeholder="Tell us your favorite films..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
            />
          </div>

          <button className="large-gradient-btn auth-submit-btn" disabled={loading} style={{ marginTop: '20px' }}>
            {loading ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>
    </div>
  );
}