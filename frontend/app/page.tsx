import Image from "next/image";
import Link from "next/link";
export default function Home() {

  let mapData = [
    {
      state: "Mumbai",
      img: "./images/map-mumbai.jpg"
    },
    {
      state: "Delhi",
      img: "/images/map-delhi.jpg"
    },
    {
      state: "Banglore",
      img: "/images/map-banglore.jpg"
    },
    {
      state: "Kolkata",
      img: "/images/map-kolkata.jpg"
    },
    {
      state: "Chennai",
      img: "/images/map-chennai.jpg"
    }
  ]



  let complaintCard = [
    {
      dept: "Water Supply",
      img: "./images/map-mumbai.jpg"
    }

  ]

  return (
    <div className="container mx-auto px-2">

      <div className="  xl:w-[1200px] rounded-[20px] sm:rounded-[50px] overflow-hidden mx-auto" >
        <div className=" h-[620px] flex items-start sm:items-center sm:h-fit p-3 sm:p-10" style={{ background: 'url("https://cdn.pixabay.com/photo/2020/04/21/03/17/mumbai-5070603_1280.jpg")', backgroundSize: "cover" }}  >

          <div className=" mt-20 sm:mt-0 " >
            <div className=" p-5 lg:max-w-[480px] rounded-[20px] bg-[#ffffffde] sm:p-10 sm:px-12 " >
              <div className="bg-[#434343] flex  p-1 items-center justify-center text-white   rounded-[40px] gap-2 " >
                <h4 className="p-1 px-2 bg-[#5c5c5c] sm:px-3 rounded-[40px]" >
                  100+ Citizen reported today
                </h4>

                <div>
                  <button className="cursor-pointer flex items-center" >Report <svg className="ml-2 w-[15px]" width="56" height="45" viewBox="0 0 56 45" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M31.7871 0.878679C32.9587 -0.292893 34.8577 -0.292893 36.0293 0.878679L55.1211 19.9705C56.2927 21.1421 56.2927 23.0411 55.1211 24.2127L36.0293 43.3045C34.8577 44.476 32.9587 44.476 31.7871 43.3045C30.6155 42.1329 30.6155 40.2338 31.7871 39.0623L45.7578 25.0916L0 25.0916L5.24537e-07 19.0916L45.7578 19.0916L31.7871 5.12087C30.6155 3.94929 30.6155 2.05025 31.7871 0.878679Z" fill="white" />
                  </svg>   </button>


                </div>
              </div>





              <div>
                <h1 className="py-6 text-4xl sm:text-5xl font-bold polysans" >
                  Connect With Mumbai. Make Your Voice Heard
                </h1>
                <p className="text-lg" >
                  Instantly report civic issues, track updates in real-time, and help build a cleaner, safer, and smarter city. Raise complaints, share feedback, and join a community working to create impact.
                </p>

                <div className="mt-6 flex gap-2 text-white" >
                  <Link href="./registerComplaint" className="" >
                    <button className="p-2 cursor-pointer rounded-[20px] p-1 px-4 bg-[#00BCD4]" > Report an issue </button>
                  
                  </Link>
                  <Link href="./administrator" >
                    <button className="p-2 cursor-pointer rounded-[20px] p-1 px-4 bg-[#37363B]" > See Live Reports  </button>
                  
                  </Link>
                </div>

              </div>
            </div>

          </div>

        </div>

      </div>



      <div className="my-30">

        <h1 className="image-text text-[170px] hidden text-center my-40 mb-20 polysans  font-bold uppercase" style={{ lineHeight: "120px" }} >
          citizen <br /> connect
        </h1>
        <div className="flex justify-center ">
          <img className="rounded-4xl  lg:w-[800px] overflow-hidden" src="/images/ct.jpg" alt="" />

        </div>

        <div className="flex justify-center mt-6" >
          <Link href="./registerComplaint" >
            <button className="p-2 text-xl   text-white cursor-pointer rounded-[40px] p-3 px-6 bg-[#00BCD4]" >Fill Your Complaint Now</button>
          
          </Link>

        </div>

      </div>


      <div className="xl:w-[1200px] rounded-[50px]   mb-20  mx-auto bg-[#DEE1E6] p-2 py-1 sm:p-10 "  >
        <h1 className="text-center mt-10 font-medium  text-4xl sm:text-5xl " >Cities in Action. Right Now</h1>
        <h2 className="text-center text-2xl mt-3" >See live reports from across India</h2>

        <div className="mt-8 flex flex-wrap justify-center gap-3 " >
          {
            mapData.map((element, index) => (
              <div className="rounded-[20px] w-full lg:w-[30%]   bg-[#f4f4f4] p-2" style={{ boxShadow: "0 6px 18px rgb(216 242 255 / 14%)" }} >
                <div className="rounded-[20px] h-[200px] w-full overflow-hidden" >
                  <img className="w-full" src={element.img} alt="" />

                </div>

                <p className="text-center font-medium text-lg text-[#444D56] p-2" > {element.state} </p>
              </div>
            ))
          }
        </div>
      </div>


      <div className="xl:w-[1200px] mx-auto mt-20 hidden" >
        <h1 className="text-center mt-10 text-5xl font-medium " >Select a Service to Report an issue</h1>


        <div className="flex" >
          {

          }

        </div>
      </div>


    </div>
  );
}
