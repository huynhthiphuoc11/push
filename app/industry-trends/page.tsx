

"use client";
import { FaRobot, FaCloud, FaLock, FaCogs, FaChartBar, FaDatabase, FaNetworkWired, FaBitcoin, FaVrCardboard, FaServer, FaAtom, FaHome, FaLeaf, FaMicrochip } from "react-icons/fa";
import { Bar } from "react-chartjs-2";
import { Chart, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
Chart.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const trends = [
  {
    icon: <FaRobot className="text-purple-600 text-4xl mb-2" />,
    title: "Artificial Intelligence (AI) & Machine Learning",
    desc: "AI and ML are transforming business operations, from automation to smart data analytics.",
    value: 95,
  },
  {
    icon: <FaCloud className="text-blue-500 text-4xl mb-2" />,
    title: "Cloud Computing",
    desc: "Cloud enables flexibility, cost savings, and scalability for modern enterprises.",
    value: 90,
  },
  {
    icon: <FaCogs className="text-green-500 text-4xl mb-2" />,
    title: "DevOps & Automation",
    desc: "DevOps fosters collaboration and accelerates software delivery.",
    value: 85,
  },
  {
    icon: <FaLock className="text-red-500 text-4xl mb-2" />,
    title: "Cybersecurity",
    desc: "Security is a top priority with increasing digital threats and compliance requirements.",
    value: 80,
  },
  {
    icon: <FaChartBar className="text-yellow-500 text-4xl mb-2" />,
    title: "Big Data Analytics",
    desc: "Big Data helps organizations extract value from massive datasets for better decisions.",
    value: 75,
  },
  {
    icon: <FaDatabase className="text-indigo-500 text-4xl mb-2" />,
    title: "No-code/Low-code Development",
    desc: "No-code/Low-code empowers rapid app creation without deep programming knowledge.",
    value: 70,
  },
  {
    icon: <FaNetworkWired className="text-teal-500 text-4xl mb-2" />,
    title: "Internet of Things (IoT)",
    desc: "IoT connects smart devices, enabling new applications in daily life and industry.",
    value: 65,
  },
  {
    icon: <FaBitcoin className="text-yellow-600 text-4xl mb-2" />,
    title: "Blockchain & Cryptocurrency",
    desc: "Blockchain technology is revolutionizing finance, supply chain, and digital identity.",
    value: 60,
  },
  {
    icon: <FaVrCardboard className="text-pink-500 text-4xl mb-2" />,
    title: "AR/VR & Immersive Tech",
    desc: "Augmented and Virtual Reality are changing entertainment, education, and remote work.",
    value: 55,
  },
  {
    icon: <FaServer className="text-gray-700 text-4xl mb-2" />,
    title: "Edge Computing",
    desc: "Edge computing brings data processing closer to devices, reducing latency and enabling real-time apps.",
    value: 50,
  },
  {
    icon: <FaAtom className="text-blue-700 text-4xl mb-2" />,
    title: "Quantum Computing",
    desc: "Quantum computers promise breakthroughs in cryptography, simulation, and optimization.",
    value: 45,
  },
  {
    icon: <FaHome className="text-orange-500 text-4xl mb-2" />,
    title: "Remote Work Tech",
    desc: "Remote work tools and platforms are reshaping how teams collaborate globally.",
    value: 40,
  },
  {
    icon: <FaLeaf className="text-green-700 text-4xl mb-2" />,
    title: "Green IT & Sustainability",
    desc: "Green IT focuses on energy efficiency, e-waste reduction, and sustainable tech solutions.",
    value: 35,
  },
  {
    icon: <FaMicrochip className="text-cyan-600 text-4xl mb-2" />,
    title: "Cyber-Physical Systems",
    desc: "Integration of physical processes with computation and networking for smart manufacturing and infrastructure.",
    value: 30,
  },
];

const chartData = {
  labels: trends.map((t) => t.title),
  datasets: [
    {
      label: "Trend Popularity (%)",
      data: trends.map((t) => t.value),
      backgroundColor: [
        "#a78bfa", "#60a5fa", "#34d399", "#f87171", "#fbbf24", "#6366f1", "#14b8a6",
        "#fde68a", "#f472b6", "#9ca3af", "#3b82f6", "#fb923c", "#22c55e", "#06b6d4"
      ],
      borderRadius: 8,
    },
  ],
};

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    title: {
      display: true,
      text: "Global IT Industry Trends Popularity (2025)",
      font: { size: 20 },
      color: "#7c3aed",
    },
  },
  scales: {
    x: {
      ticks: { color: "#6b7280", font: { size: 14 } },
      grid: { display: false },
    },
    y: {
      beginAtZero: true,
      max: 100,
      ticks: { color: "#6b7280", font: { size: 14 } },
      grid: { color: "#e5e7eb" },
    },
  },
};


export default function IndustryTrendsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-white py-16 px-4">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-5xl font-bold text-center text-purple-700 mb-6 font-sans drop-shadow-lg">IT Industry Trends 2025</h1>
        <p className="mb-10 text-xl text-gray-700 text-center font-sans">
          Discover the most prominent global trends in Information Technology, helping you shape your career and stay ahead in the tech world.
        </p>
        <div className="mb-12 bg-white rounded-xl shadow-lg p-8">
          <Bar data={chartData} options={chartOptions} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {trends.map((trend, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-lg p-6 flex flex-col items-center hover:scale-105 transition-transform duration-200">
              {trend.icon}
              <h2 className="text-xl font-bold text-gray-800 mb-2 text-center font-sans">{trend.title}</h2>
              <p className="text-gray-600 text-center font-sans">{trend.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
